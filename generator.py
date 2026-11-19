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

def run_phase_8():
    print("--- Running Phase 8: Chaos Injection Engine & Live Metrics Controller ---")

    commit("feat(chaos): define ChaosInjectionCommand request model", {
        "backend/src/main/java/com/minipayment/chaos/ChaosInjectionCommand.java": """package com.minipayment.chaos;

import com.minipayment.domain.enums.BankRail;

public class ChaosInjectionCommand {
    private BankRail rail;
    private boolean forcedOutage;
    private int additionalLatencyMs;
    private int failureRateOverridePercent;

    public BankRail getRail() { return rail; }
    public void setRail(BankRail rail) { this.rail = rail; }
    public boolean isForcedOutage() { return forcedOutage; }
    public void setForcedOutage(boolean forcedOutage) { this.forcedOutage = forcedOutage; }
    public int getAdditionalLatencyMs() { return additionalLatencyMs; }
    public void setAdditionalLatencyMs(int additionalLatencyMs) { this.additionalLatencyMs = additionalLatencyMs; }
    public int getFailureRateOverridePercent() { return failureRateOverridePercent; }
    public void setFailureRateOverridePercent(int failureRateOverridePercent) { this.failureRateOverridePercent = failureRateOverridePercent; }
}
"""
    })

    commit("feat(chaos): implement ChaosSimulatorService controlling simulated outage state across bank adapters", {
        "backend/src/main/java/com/minipayment/chaos/ChaosSimulatorService.java": """package com.minipayment.chaos;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.BankRailAdapter;
import com.minipayment.rail.BankRailRegistry;
import com.minipayment.rail.BaseBankRailAdapter;
import com.minipayment.resilience.CircuitBreakerRegistryBridge;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class ChaosSimulatorService {
    private static final Logger log = LoggerFactory.getLogger(ChaosSimulatorService.class);

    private final BankRailRegistry railRegistry;
    private final CircuitBreakerRegistryBridge circuitBreakerBridge;

    public ChaosSimulatorService(BankRailRegistry railRegistry, CircuitBreakerRegistryBridge circuitBreakerBridge) {
        this.railRegistry = railRegistry;
        this.circuitBreakerBridge = circuitBreakerBridge;
    }

    public void applyChaos(ChaosInjectionCommand cmd) {
        BankRailAdapter adapter = railRegistry.getAdapter(cmd.getRail());
        if (adapter instanceof BaseBankRailAdapter base) {
            base.setForcedOutage(cmd.isForcedOutage());
            base.setForcedLatencyMs(cmd.getAdditionalLatencyMs());
            base.setFailureRateOverridePercent(cmd.getFailureRateOverridePercent());

            if (cmd.isForcedOutage()) {
                circuitBreakerBridge.transitionToOpen(cmd.getRail());
                log.warn("CHAOS: Rail {} set to FORCED OUTAGE, Circuit Breaker forcefully tripped OPEN", cmd.getRail());
            } else if (!cmd.isForcedOutage() && circuitBreakerBridge.getState(cmd.getRail()).name().equals("OPEN")) {
                circuitBreakerBridge.transitionToClosed(cmd.getRail());
                log.info("CHAOS: Rail {} restored, Circuit Breaker reset to CLOSED", cmd.getRail());
            }
        }
    }

    public Map<String, Object> getChaosStatus() {
        Map<String, Object> status = new HashMap<>();
        for (BankRail rail : BankRail.values()) {
            BankRailAdapter adapter = railRegistry.getAdapter(rail);
            if (adapter instanceof BaseBankRailAdapter base) {
                Map<String, Object> r = new HashMap<>();
                r.put("forcedOutage", base.isForcedOutage());
                r.put("forcedLatencyMs", base.getForcedLatencyMs());
                r.put("failureRateOverridePercent", base.getFailureRateOverridePercent());
                status.put(rail.name(), r);
            }
        }
        return status;
    }

    public void resetAllChaos() {
        for (BankRail rail : BankRail.values()) {
            BankRailAdapter adapter = railRegistry.getAdapter(rail);
            if (adapter instanceof BaseBankRailAdapter base) {
                base.setForcedOutage(false);
                base.setForcedLatencyMs(0);
                base.setFailureRateOverridePercent(-1);
                circuitBreakerBridge.transitionToClosed(rail);
            }
        }
        log.info("CHAOS: All rails reset to healthy state.");
    }
}
"""
    })

    commit("feat(api): create ChaosController exposing outage simulation and recovery endpoints", {
        "backend/src/main/java/com/minipayment/controller/ChaosController.java": """package com.minipayment.controller;

import com.minipayment.chaos.ChaosInjectionCommand;
import com.minipayment.chaos.ChaosSimulatorService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/chaos")
public class ChaosController {
    private final ChaosSimulatorService chaosService;

    public ChaosController(ChaosSimulatorService chaosService) {
        this.chaosService = chaosService;
    }

    @PostMapping("/inject")
    public ResponseEntity<Map<String, Object>> injectChaos(@RequestBody ChaosInjectionCommand command) {
        chaosService.applyChaos(command);
        return ResponseEntity.ok(Map.of("message", "Chaos applied successfully", "status", chaosService.getChaosStatus()));
    }

    @PostMapping("/reset")
    public ResponseEntity<Map<String, Object>> resetAll() {
        chaosService.resetAllChaos();
        return ResponseEntity.ok(Map.of("message", "All chaos overrides reset", "status", chaosService.getChaosStatus()));
    }

    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getStatus() {
        return ResponseEntity.ok(chaosService.getChaosStatus());
    }
}
"""
    })

    commit("feat(api): create MetricsController providing live SSE stream and snapshot metrics for frontend dashboard", {
        "backend/src/main/java/com/minipayment/controller/MetricsController.java": """package com.minipayment.controller;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.resilience.CircuitBreakerRegistryBridge;
import com.minipayment.resilience.RedisSlidingWindowTracker;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/api/v1/metrics")
public class MetricsController {
    private final RedisSlidingWindowTracker windowTracker;
    private final CircuitBreakerRegistryBridge cbBridge;
    private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();

    public MetricsController(RedisSlidingWindowTracker windowTracker, CircuitBreakerRegistryBridge cbBridge) {
        this.windowTracker = windowTracker;
        this.cbBridge = cbBridge;

        Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate(this::broadcastMetrics, 1, 1, TimeUnit.SECONDS);
    }

    @GetMapping("/snapshot")
    public ResponseEntity<List<Map<String, Object>>> getSnapshot() {
        return ResponseEntity.ok(collectMetrics());
    }

    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamMetrics() {
        SseEmitter emitter = new SseEmitter(180_000L);
        emitters.add(emitter);
        emitter.onCompletion(() -> emitters.remove(emitter));
        emitter.onTimeout(() -> emitters.remove(emitter));
        return emitter;
    }

    private List<Map<String, Object>> collectMetrics() {
        List<Map<String, Object>> list = new ArrayList<>();
        for (BankRail rail : BankRail.values()) {
            Map<String, Object> m = new HashMap<>();
            m.put("rail", rail.name());
            m.put("gatewayName", rail.getGatewayName());
            m.put("successRate", windowTracker.getSuccessRate(rail));
            m.put("p90LatencyMs", windowTracker.getP90LatencyMs(rail));
            m.put("sampleSize", windowTracker.getSampleSize(rail));
            m.put("circuitState", cbBridge.getState(rail).name());
            list.add(m);
        }
        return list;
    }

    private void broadcastMetrics() {
        List<Map<String, Object>> data = collectMetrics();
        for (SseEmitter emitter : emitters) {
            try {
                emitter.send(SseEmitter.event().name("metrics").data(data));
            } catch (IOException e) {
                emitters.remove(emitter);
            }
        }
    }
}
"""
    })

    print("Phase 8 complete.")

if __name__ == "__main__":
    run_phase_8()
