package com.minipayment.resilience;

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
