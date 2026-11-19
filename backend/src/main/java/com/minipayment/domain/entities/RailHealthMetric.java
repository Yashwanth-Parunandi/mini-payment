package com.minipayment.domain.entities;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.enums.CircuitBreakerState;
import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "rail_health_metrics")
public class RailHealthMetric {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private BankRail rail;

    @Column(nullable = false)
    private double successRate;

    @Column(nullable = false)
    private long p90LatencyMs;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private CircuitBreakerState circuitBreakerState;

    @Column(nullable = false)
    private Instant recordedAt = Instant.now();

    public RailHealthMetric() {}

    public RailHealthMetric(BankRail rail, double successRate, long p90LatencyMs, CircuitBreakerState state) {
        this.rail = rail;
        this.successRate = successRate;
        this.p90LatencyMs = p90LatencyMs;
        this.circuitBreakerState = state;
        this.recordedAt = Instant.now();
    }

    public UUID getId() { return id; }
    public BankRail getRail() { return rail; }
    public double getSuccessRate() { return successRate; }
    public long getP90LatencyMs() { return p90LatencyMs; }
    public CircuitBreakerState getCircuitBreakerState() { return circuitBreakerState; }
    public Instant getRecordedAt() { return recordedAt; }
}
