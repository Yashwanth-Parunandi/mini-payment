package com.minipayment.controller;

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
