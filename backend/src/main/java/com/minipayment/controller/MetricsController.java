package com.minipayment.controller;

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
