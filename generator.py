import os
import subprocess
import sys

def commit(msg, files_dict):
    for rel_path, content in files_dict.items():
        full_path = os.path.abspath(rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", msg, "--quiet"], check=True)
    
    res = subprocess.run(["git", "rev-list", "--count", "HEAD"], capture_output=True, text=True, check=True)
    count = res.stdout.strip()
    print(f"[{count}] {msg}")

def run_phase_5():
    print("--- Running Phase 5: Sliding-Window Metrics & Circuit Breaker Engine ---")

    commit("feat(resilience): add SlidingWindowCallMetric model for ring buffer samples", {
        "backend/src/main/java/com/minipayment/resilience/SlidingWindowCallMetric.java": """package com.minipayment.resilience;

import java.io.Serializable;
import java.time.Instant;

public class SlidingWindowCallMetric implements Serializable {
    private final boolean success;
    private final long latencyMs;
    private final Instant timestamp;

    public SlidingWindowCallMetric(boolean success, long latencyMs) {
        this.success = success;
        this.latencyMs = latencyMs;
        this.timestamp = Instant.now();
    }

    public boolean isSuccess() { return success; }
    public long getLatencyMs() { return latencyMs; }
    public Instant getTimestamp() { return timestamp; }
}
"""
    })

    commit("feat(resilience): implement RedisSlidingWindowTracker for distributed state counting", {
        "backend/src/main/java/com/minipayment/resilience/RedisSlidingWindowTracker.java": """package com.minipayment.resilience;

import com.minipayment.domain.enums.BankRail;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedDeque;

@Component
public class RedisSlidingWindowTracker {
    private static final int WINDOW_SIZE = 50;
    private final RedisTemplate<String, Object> redisTemplate;

    // In-memory sliding window fallback for low latency
    private final Map<BankRail, Deque<SlidingWindowCallMetric>> localWindows = new ConcurrentHashMap<>();

    public RedisSlidingWindowTracker(RedisTemplate<String, Object> redisTemplate) {
        this.redisTemplate = redisTemplate;
        for (BankRail rail : BankRail.values()) {
            localWindows.put(rail, new ConcurrentLinkedDeque<>());
        }
    }

    public void recordCall(BankRail rail, boolean success, long latencyMs) {
        Deque<SlidingWindowCallMetric> window = localWindows.get(rail);
        window.addLast(new SlidingWindowCallMetric(success, latencyMs));
        while (window.size() > WINDOW_SIZE) {
            window.pollFirst();
        }

        try {
            String redisKey = "metrics:rail:" + rail.name();
            redisTemplate.opsForList().rightPush(redisKey, success ? "1:" + latencyMs : "0:" + latencyMs);
            redisTemplate.opsForList().trim(redisKey, -WINDOW_SIZE, -1);
        } catch (Exception ignored) {
            // Local fallback continues uninterrupted
        }
    }

    public double getSuccessRate(BankRail rail) {
        Deque<SlidingWindowCallMetric> window = localWindows.get(rail);
        if (window == null || window.isEmpty()) {
            return 100.0;
        }
        long successCount = window.stream().filter(SlidingWindowCallMetric::isSuccess).count();
        return (double) successCount / window.size() * 100.0;
    }

    public long getP90LatencyMs(BankRail rail) {
        Deque<SlidingWindowCallMetric> window = localWindows.get(rail);
        if (window == null || window.isEmpty()) {
            return rail.getBaselineLatencyMs();
        }
        List<Long> latencies = window.stream()
                .map(SlidingWindowCallMetric::getLatencyMs)
                .sorted()
                .toList();
        int index = (int) Math.ceil(0.90 * latencies.size()) - 1;
        return latencies.get(Math.max(0, index));
    }

    public int getSampleSize(BankRail rail) {
        Deque<SlidingWindowCallMetric> window = localWindows.get(rail);
        return window != null ? window.size() : 0;
    }
}
"""
    })

    commit("feat(resilience): implement CircuitBreakerRegistryBridge connecting Resilience4j instances", {
        "backend/src/main/java/com/minipayment/resilience/CircuitBreakerRegistryBridge.java": """package com.minipayment.resilience;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.enums.CircuitBreakerState;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class CircuitBreakerRegistryBridge {
    private final CircuitBreakerRegistry circuitBreakerRegistry;
    private final Map<BankRail, CircuitBreaker> railCircuitBreakerMap = new ConcurrentHashMap<>();

    public CircuitBreakerRegistryBridge(CircuitBreakerRegistry circuitBreakerRegistry) {
        this.circuitBreakerRegistry = circuitBreakerRegistry;
        registerRail(BankRail.HDFC_RAIL, "hdfc-rail");
        registerRail(BankRail.ICICI_RAIL, "icici-rail");
        registerRail(BankRail.SBI_RAIL, "sbi-rail");
        registerRail(BankRail.AXIS_UPI_RAIL, "axis-rail");
    }

    private void registerRail(BankRail rail, String configName) {
        CircuitBreaker cb = circuitBreakerRegistry.circuitBreaker(configName);
        railCircuitBreakerMap.put(rail, cb);
    }

    public CircuitBreaker getCircuitBreaker(BankRail rail) {
        return railCircuitBreakerMap.get(rail);
    }

    public CircuitBreakerState getState(BankRail rail) {
        CircuitBreaker cb = railCircuitBreakerMap.get(rail);
        if (cb == null) return CircuitBreakerState.CLOSED;

        CircuitBreaker.State state = cb.getState();
        return switch (state) {
            case OPEN, FORCED_OPEN -> CircuitBreakerState.OPEN;
            case HALF_OPEN -> CircuitBreakerState.HALF_OPEN;
            default -> CircuitBreakerState.CLOSED;
        };
    }

    public void transitionToOpen(BankRail rail) {
        CircuitBreaker cb = railCircuitBreakerMap.get(rail);
        if (cb != null) {
            cb.transitionToOpenState();
        }
    }

    public void transitionToClosed(BankRail rail) {
        CircuitBreaker cb = railCircuitBreakerMap.get(rail);
        if (cb != null) {
            cb.transitionToClosedState();
        }
    }
}
"""
    })

    commit("feat(resilience): add CircuitBreakerEventListener publishing transition events", {
        "backend/src/main/java/com/minipayment/resilience/CircuitBreakerEventListener.java": """package com.minipayment.resilience;

import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import io.github.resilience4j.circuitbreaker.event.CircuitBreakerOnStateTransitionEvent;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Component;

@Component
public class CircuitBreakerEventListener {
    private static final Logger log = LoggerFactory.getLogger(CircuitBreakerEventListener.class);

    private final CircuitBreakerRegistry circuitBreakerRegistry;
    private final ApplicationEventPublisher eventPublisher;

    public CircuitBreakerEventListener(CircuitBreakerRegistry circuitBreakerRegistry, ApplicationEventPublisher eventPublisher) {
        this.circuitBreakerRegistry = circuitBreakerRegistry;
        this.eventPublisher = eventPublisher;
    }

    @PostConstruct
    public void registerListeners() {
        circuitBreakerRegistry.getAllCircuitBreakers().forEach(cb -> {
            cb.getEventPublisher().onStateTransition(this::handleStateTransition);
        });
    }

    private void handleStateTransition(CircuitBreakerOnStateTransitionEvent event) {
        log.warn("CIRCUIT BREAKER STATE CHANGE: '{}' transitioned from {} to {}",
                event.getCircuitBreakerName(),
                event.getStateTransition().getFromState(),
                event.getStateTransition().getToState());
        eventPublisher.publishEvent(event);
    }
}
"""
    })

    print("Phase 5 complete.")

if __name__ == "__main__":
    run_phase_5()
