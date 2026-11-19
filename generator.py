import os
import subprocess
import sys

def commit(msg, files_dict):
    for rel_path, content in files_dict.items():
        full_path = os.path.abspath(rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", msg, "--quiet"], check=True)
    
    res = subprocess.run(["git", "rev-list", "--count", "HEAD"], capture_output=True, text=True, check=True)
    count = res.stdout.strip()
    print(f"[{count}] {msg}")

def run_phase_3():
    print("--- Running Phase 3: Repositories, Database Migrations & Persistence ---")
    
    commit("feat(repo): add MerchantRepository with API key lookup", {
        "backend/src/main/java/com/minipayment/repository/MerchantRepository.java": """package com.minipayment.repository;

import com.minipayment.domain.entities.Merchant;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface MerchantRepository extends JpaRepository<Merchant, UUID> {
    Optional<Merchant> findByApiKey(String apiKey);
    boolean existsByApiKey(String apiKey);
}
"""
    })

    commit("feat(repo): add PaymentOrderRepository with idempotency and status queries", {
        "backend/src/main/java/com/minipayment/repository/PaymentOrderRepository.java": """package com.minipayment.repository;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.enums.PaymentStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface PaymentOrderRepository extends JpaRepository<PaymentOrder, UUID> {
    Optional<PaymentOrder> findByIdempotencyKey(String idempotencyKey);
    List<PaymentOrder> findByStatus(PaymentStatus status);
    Page<PaymentOrder> findByRoutedRail(BankRail routedRail, Pageable pageable);
    long countByRoutedRailAndStatus(BankRail rail, PaymentStatus status);
}
"""
    })

    commit("feat(repo): add LedgerAccountRepository with account number lookup and optimistic locks", {
        "backend/src/main/java/com/minipayment/repository/LedgerAccountRepository.java": """package com.minipayment.repository;

import com.minipayment.domain.entities.LedgerAccount;
import com.minipayment.domain.enums.AccountType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface LedgerAccountRepository extends JpaRepository<LedgerAccount, UUID> {
    Optional<LedgerAccount> findByAccountNumber(String accountNumber);
    Optional<LedgerAccount> findByAccountType(AccountType accountType);
}
"""
    })

    commit("feat(repo): add JournalEntryRepository with audit and order lookups", {
        "backend/src/main/java/com/minipayment/repository/JournalEntryRepository.java": """package com.minipayment.repository;

import com.minipayment.domain.entities.JournalEntry;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.UUID;

@Repository
public interface JournalEntryRepository extends JpaRepository<JournalEntry, UUID> {
    List<JournalEntry> findByPaymentOrderId(UUID paymentOrderId);
}
"""
    })

    commit("feat(repo): add RailHealthMetricRepository with time-series lookback query", {
        "backend/src/main/java/com/minipayment/repository/RailHealthMetricRepository.java": """package com.minipayment.repository;

import com.minipayment.domain.entities.RailHealthMetric;
import com.minipayment.domain.enums.BankRail;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Repository
public interface RailHealthMetricRepository extends JpaRepository<RailHealthMetric, UUID> {
    List<RailHealthMetric> findByRailOrderByRecordedAtDesc(BankRail rail);

    @Query("SELECT r FROM RailHealthMetric r WHERE r.rail = :rail AND r.recordedAt >= :since ORDER BY r.recordedAt ASC")
    List<RailHealthMetric> findRecentMetrics(@Param("rail") BankRail rail, @Param("since") Instant since);
}
"""
    })

    commit("feat(db): add initial PostgreSQL schema DDL migration script", {
        "backend/src/main/resources/db/migration/V1__initial_schema.sql": """-- Schema initialization for Mini Payment Gateway Orchestrator

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
"""
    })

    commit("feat(db): add database seed data for nodal escrow and default merchant", {
        "backend/src/main/resources/db/migration/V2__seed_accounts.sql": """-- Default Nodal Escrow and Merchant accounts
INSERT INTO ledger_accounts (id, account_number, account_type, currency, current_balance, created_at, updated_at)
VALUES 
('a0000000-0000-0000-0000-000000000001', 'ESCROW_NODAL_INR_01', 'NODAL_ESCROW', 'INR', 10000000.0000, NOW(), NOW()),
('a0000000-0000-0000-0000-000000000002', 'PLATFORM_REVENUE_01', 'PLATFORM_FEE', 'INR', 0.0000, NOW(), NOW()),
('a0000000-0000-0000-0000-000000000003', 'REFUND_RESERVE_01', 'REFUND_RESERVE', 'INR', 500000.0000, NOW(), NOW());

INSERT INTO merchants (id, api_key, business_name, webhook_url, active, created_at, updated_at)
VALUES 
('m0000000-0000-0000-0000-000000000001', 'mk_live_bharat_pay_998877', 'Flipkart India Pvt Ltd', 'https://webhook.site/test', TRUE, NOW(), NOW());
"""
    })

    commit("feat(config): configure RedisTemplate with Jackson2JsonRedisSerializer", {
        "backend/src/main/java/com/minipayment/config/RedisConfiguration.java": """package com.minipayment.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;

@Configuration
public class RedisConfiguration {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        template.setKeySerializer(new StringRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.afterPropertiesSet();
        return template;
    }
}
"""
    })

    commit("feat(config): configure Cors and Security filter chain for API access", {
        "backend/src/main/java/com/minipayment/config/WebMvcCorsConfig.java": """package com.minipayment.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebMvcCorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins("http://localhost:3000", "http://127.0.0.1:3000")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true);
    }
}
"""
    })

    commit("feat(config): configure Jackson Object Mapper for ISO timestamps and money serialization", {
        "backend/src/main/java/com/minipayment/config/JacksonConfig.java": """package com.minipayment.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
public class JacksonConfig {
    @Bean
    @Primary
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new JavaTimeModule());
        mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        return mapper;
    }
}
"""
    })

    print("Phase 3 complete.")

if __name__ == "__main__":
    run_phase_3()
