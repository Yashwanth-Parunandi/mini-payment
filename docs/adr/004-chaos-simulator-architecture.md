# ADR 004: Chaos Simulator Architecture for Interviewer Demonstration

## Status
Accepted

## Decision
Embed a dedicated Chaos Controller exposing real-time fault injection toggles:
- Failure rate overrides (0% to 100%)
- Latency injection (0ms to 10000ms artificial delay)
- Rail blackholing / socket disconnect simulation
- Automated recovery timer
