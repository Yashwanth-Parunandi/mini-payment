package com.minipayment.resilience;

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
