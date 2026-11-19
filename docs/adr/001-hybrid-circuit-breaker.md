# ADR 001: Hybrid Sliding-Window Circuit Breakers for Bank Rails

## Status
Accepted

## Context
UPI and Bank payment rails in high-volume markets (India) experience localized transient outages, packet drops, and high latency surges (P99 > 8s). Standard static routing leads to high transaction failure rates (>15%).

## Decision
We implement a hybrid sliding-window circuit breaker backed by Resilience4j and Redis for multi-pod state synchronization:
1. Closed State: Normal operation, traffic routed based on optimal health weight.
2. Open State: Triggered when failure rate exceeds 20% over a 50-request window or P95 latency > 2500ms.
3. Half-Open State: Canary probes (5% traffic) after cool-down period of 15 seconds.

## Consequences
- Requires Redis for atomic counter increments and state synchronization.
- Failover latency reduced to < 5ms upon threshold breach.
