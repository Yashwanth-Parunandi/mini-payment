# ADR 002: Dynamic Multi-Rail Routing Algorithm

## Status
Accepted

## Context
When multiple payment gateways support a requested payment method (UPI / Card / NetBanking), traffic allocation should optimize for:
1. Availability / Success rate (weight: 0.6)
2. Average Latency (weight: 0.25)
3. Merchant Commercial Cost (weight: 0.15)

## Decision
Dynamic Route Score formula:
Score = (SuccessRate * 60) + ((MaxLatency - P90Latency) / MaxLatency * 25) + ((MaxCost - Cost) / MaxCost * 15)

The engine routes to the highest score rail whose Circuit Breaker is CLOSED or HALF-OPEN.
