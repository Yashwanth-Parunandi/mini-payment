package com.minipayment.domain.entities;

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
