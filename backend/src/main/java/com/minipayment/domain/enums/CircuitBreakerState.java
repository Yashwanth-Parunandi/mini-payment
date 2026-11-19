package com.minipayment.domain.enums;

public enum CircuitBreakerState {
    CLOSED("Operating Normally - Receiving Full Traffic"),
    HALF_OPEN("Trial Probes Active - Low Volume Traffic"),
    OPEN("Fault Threshold Breached - Outage Isolated");

    private final String description;

    CircuitBreakerState(String description) {
        this.description = description;
    }

    public String getDescription() { return description; }
}
