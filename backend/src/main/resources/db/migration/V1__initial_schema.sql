-- Schema initialization for Mini Payment Gateway Orchestrator

CREATE TABLE merchants (
    id UUID PRIMARY KEY,
    api_key VARCHAR(128) NOT NULL UNIQUE,
    business_name VARCHAR(255) NOT NULL,
    webhook_url VARCHAR(512) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE payment_orders (
    id UUID PRIMARY KEY,
    merchant_order_id VARCHAR(128) NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    amount NUMERIC(19, 4) NOT NULL,
    currency VARCHAR(16) NOT NULL,
    payment_method VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    routed_rail VARCHAR(32),
    attempt_count INT DEFAULT 0,
    error_reason TEXT,
    latency_ms BIGINT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_payment_orders_status ON payment_orders(status);
CREATE INDEX idx_payment_orders_rail ON payment_orders(routed_rail);
CREATE INDEX idx_payment_orders_idempotency ON payment_orders(idempotency_key);

CREATE TABLE ledger_accounts (
    id UUID PRIMARY KEY,
    account_number VARCHAR(64) NOT NULL UNIQUE,
    account_type VARCHAR(32) NOT NULL,
    currency VARCHAR(16) NOT NULL,
    current_balance NUMERIC(19, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE journal_entries (
    id UUID PRIMARY KEY,
    payment_order_id UUID NOT NULL,
    ledger_account_id UUID NOT NULL REFERENCES ledger_accounts(id),
    entry_type VARCHAR(16) NOT NULL,
    amount NUMERIC(19, 4) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_journal_entries_order ON journal_entries(payment_order_id);

CREATE TABLE rail_health_metrics (
    id UUID PRIMARY KEY,
    rail VARCHAR(32) NOT NULL,
    success_rate DOUBLE PRECISION NOT NULL,
    p90_latency_ms BIGINT NOT NULL,
    circuit_breaker_state VARCHAR(32) NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_rail_health_metrics_rail_time ON rail_health_metrics(rail, recorded_at);
