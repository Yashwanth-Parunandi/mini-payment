package com.minipayment.dto;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.enums.PaymentStatus;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

public class PaymentResponse {
    private UUID paymentId;
    private String merchantOrderId;
    private String idempotencyKey;
    private BigDecimal amount;
    private String currency;
    private PaymentStatus status;
    private BankRail routedRail;
    private Long latencyMs;
    private String errorReason;
    private Instant createdAt;

    public static PaymentResponse from(PaymentOrder order) {
        PaymentResponse res = new PaymentResponse();
        res.paymentId = order.getId();
        res.merchantOrderId = order.getMerchantOrderId();
        res.idempotencyKey = order.getIdempotencyKey();
        res.amount = order.getAmount();
        res.currency = order.getCurrency().name();
        res.status = order.getStatus();
        res.routedRail = order.getRoutedRail();
        res.latencyMs = order.getLatencyMs();
        res.errorReason = order.getErrorReason();
        res.createdAt = order.getCreatedAt();
        return res;
    }

    public UUID getPaymentId() { return paymentId; }
    public String getMerchantOrderId() { return merchantOrderId; }
    public String getIdempotencyKey() { return idempotencyKey; }
    public BigDecimal getAmount() { return amount; }
    public String getCurrency() { return currency; }
    public PaymentStatus getStatus() { return status; }
    public BankRail getRoutedRail() { return routedRail; }
    public Long getLatencyMs() { return latencyMs; }
    public String getErrorReason() { return errorReason; }
    public Instant getCreatedAt() { return createdAt; }
}
