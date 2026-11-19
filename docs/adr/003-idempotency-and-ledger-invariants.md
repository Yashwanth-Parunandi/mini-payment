# ADR 003: Idempotency Key Specification and Double-Entry Ledger Invariant

## Status
Accepted

## Context
Network timeouts frequently cause merchants to retry transaction requests. Retrying without strict idempotency risks duplicate debit operations.

## Decision
1. Merchants must provide an `Idempotency-Key` header with UUIDv4.
2. Stored in Redis with 120-second active lock and PostgreSQL with 24-hour retention.
3. Every transaction strictly updates a double-entry journal balance (Customer Account vs Merchant Holding Account).
