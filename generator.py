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

def run_phase_2():
    print("--- Running Phase 2: Domain Layer Entities, Enums & Value Objects ---")
    
    commit("feat(domain): add Currency enum with ISO codes and minor unit precisions", {
        "backend/src/main/java/com/minipayment/domain/enums/Currency.java": """package com.minipayment.domain.enums;

public enum Currency {
    INR("Indian Rupee", 2),
    USD("US Dollar", 2),
    EUR("Euro", 2),
    GBP("British Pound", 2),
    SGD("Singapore Dollar", 2);

    private final String description;
    private final int minorUnitFraction;

    Currency(String description, int minorUnitFraction) {
        this.description = description;
        this.minorUnitFraction = minorUnitFraction;
    }

    public String getDescription() { return description; }
    public int getMinorUnitFraction() { return minorUnitFraction; }
}
"""
    })

    commit("feat(domain): add immutable Money value object with arithmetic invariants", {
        "backend/src/main/java/com/minipayment/domain/valueobjects/Money.java": """package com.minipayment.domain.valueobjects;

import com.minipayment.domain.enums.Currency;
import java.io.Serializable;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Objects;

public final class Money implements Serializable, Comparable<Money> {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) {
        Objects.requireNonNull(amount, "Amount cannot be null");
        Objects.requireNonNull(currency, "Currency cannot be null");
        this.amount = amount.setScale(currency.getMinorUnitFraction(), RoundingMode.HALF_EVEN);
        this.currency = currency;
    }

    public static Money of(double amount, Currency currency) {
        return new Money(BigDecimal.valueOf(amount), currency);
    }

    public static Money inr(double amount) {
        return of(amount, Currency.INR);
    }

    public static Money zero(Currency currency) {
        return new Money(BigDecimal.ZERO, currency);
    }

    public Money add(Money other) {
        validateSameCurrency(other);
        return new Money(this.amount.add(other.amount), this.currency);
    }

    public Money subtract(Money other) {
        validateSameCurrency(other);
        return new Money(this.amount.subtract(other.amount), this.currency);
    }

    public boolean isPositive() {
        return this.amount.compareTo(BigDecimal.ZERO) > 0;
    }

    public boolean isZeroOrPositive() {
        return this.amount.compareTo(BigDecimal.ZERO) >= 0;
    }

    private void validateSameCurrency(Money other) {
        if (this.currency != other.currency) {
            throw new IllegalArgumentException("Cannot operate on different currencies: " + this.currency + " vs " + other.currency);
        }
    }

    public BigDecimal getAmount() { return amount; }
    public Currency getCurrency() { return currency; }

    @Override
    public int compareTo(Money o) {
        validateSameCurrency(o);
        return this.amount.compareTo(o.amount);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Money money = (Money) o;
        return amount.compareTo(money.amount) == 0 && currency == money.currency;
    }

    @Override
    public int hashCode() {
        return Objects.hash(amount, currency);
    }

    @Override
    public String toString() {
        return currency + " " + amount;
    }
}
"""
    })

    commit("feat(domain): add PaymentMethod enum covering UPI, Card, NetBanking and Wallets", {
        "backend/src/main/java/com/minipayment/domain/enums/PaymentMethod.java": """package com.minipayment.domain.enums;

public enum PaymentMethod {
    UPI("Unified Payments Interface", true),
    CREDIT_CARD("Credit Card Gateway", false),
    DEBIT_CARD("Debit Card Gateway", false),
    NET_BANKING("NetBanking Portal", true),
    WALLET("Digital Wallet", true);

    private final String displayName;
    private final boolean instantSettlement;

    PaymentMethod(String displayName, boolean instantSettlement) {
        this.displayName = displayName;
        this.instantSettlement = instantSettlement;
    }

    public String getDisplayName() { return displayName; }
    public boolean isInstantSettlement() { return instantSettlement; }
}
"""
    })

    commit("feat(domain): add BankRail enum for Indian PSP processors and gateways", {
        "backend/src/main/java/com/minipayment/domain/enums/BankRail.java": """package com.minipayment.domain.enums;

public enum BankRail {
    HDFC_RAIL("HDFC Bank SmartGateway", "HDFC_01", 120),
    ICICI_RAIL("ICICI Bank Corporate Rail", "ICICI_01", 140),
    SBI_RAIL("State Bank of India Core Rail", "SBI_01", 210),
    AXIS_UPI_RAIL("Axis Bank Instant UPI Rail", "AXIS_01", 90);

    private final String gatewayName;
    private final String code;
    private final int baselineLatencyMs;

    BankRail(String gatewayName, String code, int baselineLatencyMs) {
        this.gatewayName = gatewayName;
        this.code = code;
        this.baselineLatencyMs = baselineLatencyMs;
    }

    public String getGatewayName() { return gatewayName; }
    public String getCode() { return code; }
    public int getBaselineLatencyMs() { return baselineLatencyMs; }
}
"""
    })

    commit("feat(domain): add PaymentStatus lifecycle state enum", {
        "backend/src/main/java/com/minipayment/domain/enums/PaymentStatus.java": """package com.minipayment.domain.enums;

public enum PaymentStatus {
    INITIATED,
    ROUTING,
    CIRCUIT_VERIFIED,
    SUBMITTED_TO_PSP,
    SUCCESS,
    FAILED,
    RETRYING,
    TIMED_OUT,
    REFUND_REQUESTED,
    REFUNDED
}
"""
    })

    commit("feat(domain): add CircuitBreakerState enum with transitions", {
        "backend/src/main/java/com/minipayment/domain/enums/CircuitBreakerState.java": """package com.minipayment.domain.enums;

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
"""
    })

    commit("feat(domain): add LedgerEntryType enum for double-entry bookkeeping", {
        "backend/src/main/java/com/minipayment/domain/enums/LedgerEntryType.java": """package com.minipayment.domain.enums;

public enum LedgerEntryType {
    DEBIT,
    CREDIT
}
"""
    })

    commit("feat(domain): add AccountType enum for merchant, escrow, fees and nodal accounts", {
        "backend/src/main/java/com/minipayment/domain/enums/AccountType.java": """package com.minipayment.domain.enums;

public enum AccountType {
    CUSTOMER_SOURCE,
    NODAL_ESCROW,
    MERCHANT_PAYABLE,
    PLATFORM_FEE,
    GATEWAY_FEE,
    REFUND_RESERVE
}
"""
    })

    commit("feat(domain): add base AuditableEntity for JPA lifecycle tracking", {
        "backend/src/main/java/com/minipayment/domain/entities/AuditableEntity.java": """package com.minipayment.domain.entities;

import jakarta.persistence.Column;
import jakarta.persistence.MappedSuperclass;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import java.time.Instant;

@MappedSuperclass
public abstract class AuditableEntity {
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = Instant.now();
        this.updatedAt = Instant.now();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = Instant.now();
    }

    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
}
"""
    })

    commit("feat(domain): add Merchant entity with API keys and tier limits", {
        "backend/src/main/java/com/minipayment/domain/entities/Merchant.java": """package com.minipayment.domain.entities;

import jakarta.persistence.*;
import java.util.UUID;

@Entity
@Table(name = "merchants")
public class Merchant extends AuditableEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, unique = true)
    private String apiKey;

    @Column(nullable = false)
    private String businessName;

    @Column(nullable = false)
    private String webhookUrl;

    @Column(nullable = false)
    private boolean active = true;

    public Merchant() {}

    public Merchant(String businessName, String apiKey, String webhookUrl) {
        this.businessName = businessName;
        this.apiKey = apiKey;
        this.webhookUrl = webhookUrl;
    }

    public UUID getId() { return id; }
    public String getApiKey() { return apiKey; }
    public String getBusinessName() { return businessName; }
    public String getWebhookUrl() { return webhookUrl; }
    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }
}
"""
    })

    commit("feat(domain): add PaymentOrder entity tracking lifecycle, selected rail and attempts", {
        "backend/src/main/java/com/minipayment/domain/entities/PaymentOrder.java": """package com.minipayment.domain.entities;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.enums.Currency;
import com.minipayment.domain.enums.PaymentMethod;
import com.minipayment.domain.enums.PaymentStatus;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "payment_orders")
public class PaymentOrder extends AuditableEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "merchant_order_id", nullable = false)
    private String merchantOrderId;

    @Column(name = "idempotency_key", nullable = false, unique = true)
    private String idempotencyKey;

    @Column(nullable = false)
    private BigDecimal amount;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Currency currency;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PaymentMethod paymentMethod;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PaymentStatus status;

    @Enumerated(EnumType.STRING)
    @Column(name = "routed_rail")
    private BankRail routedRail;

    @Column(name = "attempt_count")
    private int attemptCount = 0;

    @Column(name = "error_reason")
    private String errorReason;

    @Column(name = "latency_ms")
    private Long latencyMs;

    public PaymentOrder() {}

    public PaymentOrder(String merchantOrderId, String idempotencyKey, BigDecimal amount, Currency currency, PaymentMethod paymentMethod) {
        this.merchantOrderId = merchantOrderId;
        this.idempotencyKey = idempotencyKey;
        this.amount = amount;
        this.currency = currency;
        this.paymentMethod = paymentMethod;
        this.status = PaymentStatus.INITIATED;
    }

    public UUID getId() { return id; }
    public String getMerchantOrderId() { return merchantOrderId; }
    public String getIdempotencyKey() { return idempotencyKey; }
    public BigDecimal getAmount() { return amount; }
    public Currency getCurrency() { return currency; }
    public PaymentMethod getPaymentMethod() { return paymentMethod; }
    public PaymentStatus getStatus() { return status; }
    public void setStatus(PaymentStatus status) { this.status = status; }
    public BankRail getRoutedRail() { return routedRail; }
    public void setRoutedRail(BankRail routedRail) { this.routedRail = routedRail; }
    public int getAttemptCount() { return attemptCount; }
    public void incrementAttemptCount() { this.attemptCount++; }
    public String getErrorReason() { return errorReason; }
    public void setErrorReason(String errorReason) { this.errorReason = errorReason; }
    public Long getLatencyMs() { return latencyMs; }
    public void setLatencyMs(Long latencyMs) { this.latencyMs = latencyMs; }
}
"""
    })

    commit("feat(domain): add LedgerAccount entity representing double-entry accounts", {
        "backend/src/main/java/com/minipayment/domain/entities/LedgerAccount.java": """package com.minipayment.domain.entities;

import com.minipayment.domain.enums.AccountType;
import com.minipayment.domain.enums.Currency;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "ledger_accounts")
public class LedgerAccount extends AuditableEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "account_number", nullable = false, unique = true)
    private String accountNumber;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AccountType accountType;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Currency currency;

    @Column(nullable = false)
    private BigDecimal currentBalance = BigDecimal.ZERO;

    public LedgerAccount() {}

    public LedgerAccount(String accountNumber, AccountType accountType, Currency currency) {
        this.accountNumber = accountNumber;
        this.accountType = accountType;
        this.currency = currency;
        this.currentBalance = BigDecimal.ZERO;
    }

    public UUID getId() { return id; }
    public String getAccountNumber() { return accountNumber; }
    public AccountType getAccountType() { return accountType; }
    public Currency getCurrency() { return currency; }
    public BigDecimal getCurrentBalance() { return currentBalance; }
    public void setCurrentBalance(BigDecimal currentBalance) { this.currentBalance = currentBalance; }
}
"""
    })

    commit("feat(domain): add JournalEntry entity capturing double-entry transaction debits and credits", {
        "backend/src/main/java/com/minipayment/domain/entities/JournalEntry.java": """package com.minipayment.domain.entities;

import com.minipayment.domain.enums.LedgerEntryType;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "journal_entries")
public class JournalEntry extends AuditableEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "payment_order_id", nullable = false)
    private UUID paymentOrderId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ledger_account_id", nullable = false)
    private LedgerAccount account;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private LedgerEntryType entryType;

    @Column(nullable = false)
    private BigDecimal amount;

    public JournalEntry() {}

    public JournalEntry(UUID paymentOrderId, LedgerAccount account, LedgerEntryType entryType, BigDecimal amount) {
        this.paymentOrderId = paymentOrderId;
        this.account = account;
        this.entryType = entryType;
        this.amount = amount;
    }

    public UUID getId() { return id; }
    public UUID getPaymentOrderId() { return paymentOrderId; }
    public LedgerAccount getAccount() { return account; }
    public LedgerEntryType getEntryType() { return entryType; }
    public BigDecimal getAmount() { return amount; }
}
"""
    })

    commit("feat(domain): add RailHealthMetric entity storing sliding-window historical logs", {
        "backend/src/main/java/com/minipayment/domain/entities/RailHealthMetric.java": """package com.minipayment.domain.entities;

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
"""
    })

    commit("feat(domain): add CustomerPaymentProfile value object with VPA and tokenized cards", {
        "backend/src/main/java/com/minipayment/domain/valueobjects/CustomerPaymentProfile.java": """package com.minipayment.domain.valueobjects;

import java.io.Serializable;

public class CustomerPaymentProfile implements Serializable {
    private final String customerId;
    private final String vpaAddress;
    private final String maskedCardNumber;
    private final String cardNetwork;

    public CustomerPaymentProfile(String customerId, String vpaAddress, String maskedCardNumber, String cardNetwork) {
        this.customerId = customerId;
        this.vpaAddress = vpaAddress;
        this.maskedCardNumber = maskedCardNumber;
        this.cardNetwork = cardNetwork;
    }

    public static CustomerPaymentProfile forUpi(String customerId, String vpa) {
        return new CustomerPaymentProfile(customerId, vpa, null, null);
    }

    public static CustomerPaymentProfile forCard(String customerId, String maskedCard, String network) {
        return new CustomerPaymentProfile(customerId, null, maskedCard, network);
    }

    public String getCustomerId() { return customerId; }
    public String getVpaAddress() { return vpaAddress; }
    public String getMaskedCardNumber() { return maskedCardNumber; }
    public String getCardNetwork() { return cardNetwork; }
}
"""
    })

    commit("feat(domain): add RouteEvaluationResult value object carrying scoring breakdown", {
        "backend/src/main/java/com/minipayment/domain/valueobjects/RouteEvaluationResult.java": """package com.minipayment.domain.valueobjects;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.enums.CircuitBreakerState;
import java.io.Serializable;

public class RouteEvaluationResult implements Serializable {
    private final BankRail selectedRail;
    private final double compositeScore;
    private final double successRate;
    private final long p90LatencyMs;
    private final CircuitBreakerState circuitState;
    private final String explanation;

    public RouteEvaluationResult(BankRail selectedRail, double compositeScore, double successRate, 
                                 long p90LatencyMs, CircuitBreakerState circuitState, String explanation) {
        this.selectedRail = selectedRail;
        this.compositeScore = compositeScore;
        this.successRate = successRate;
        this.p90LatencyMs = p90LatencyMs;
        this.circuitState = circuitState;
        this.explanation = explanation;
    }

    public BankRail getSelectedRail() { return selectedRail; }
    public double getCompositeScore() { return compositeScore; }
    public double getSuccessRate() { return successRate; }
    public long getP90LatencyMs() { return p90LatencyMs; }
    public CircuitBreakerState getCircuitState() { return circuitState; }
    public String getExplanation() { return explanation; }
}
"""
    })

    print("Phase 2 complete.")

if __name__ == "__main__":
    run_phase_2()
