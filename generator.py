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

def run_phase_7():
    print("--- Running Phase 7: Payment Orchestration, Ledger & API Layer ---")

    commit("feat(service): add LedgerService managing double-entry journal postings", {
        "backend/src/main/java/com/minipayment/service/LedgerService.java": """package com.minipayment.service;

import com.minipayment.domain.entities.JournalEntry;
import com.minipayment.domain.entities.LedgerAccount;
import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.enums.AccountType;
import com.minipayment.domain.enums.LedgerEntryType;
import com.minipayment.repository.JournalEntryRepository;
import com.minipayment.repository.LedgerAccountRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

@Service
public class LedgerService {
    private final LedgerAccountRepository accountRepository;
    private final JournalEntryRepository journalRepository;

    public LedgerService(LedgerAccountRepository accountRepository, JournalEntryRepository journalRepository) {
        this.accountRepository = accountRepository;
        this.journalRepository = journalRepository;
    }

    @Transactional
    public void recordSuccessfulPayment(PaymentOrder order) {
        LedgerAccount nodalEscrow = accountRepository.findByAccountType(AccountType.NODAL_ESCROW)
                .orElseThrow(() -> new IllegalStateException("Nodal escrow account not configured"));
        
        LedgerAccount merchantPayable = accountRepository.findByAccountType(AccountType.MERCHANT_PAYABLE)
                .orElseGet(() -> {
                    LedgerAccount acc = new LedgerAccount("MERCHANT_GENERIC_01", AccountType.MERCHANT_PAYABLE, order.getCurrency());
                    return accountRepository.save(acc);
                });

        BigDecimal amount = order.getAmount();

        // Double-entry: Debit Escrow (+ asset), Credit Merchant Payable (+ liability)
        nodalEscrow.setCurrentBalance(nodalEscrow.getCurrentBalance().add(amount));
        merchantPayable.setCurrentBalance(merchantPayable.getCurrentBalance().add(amount));

        accountRepository.save(nodalEscrow);
        accountRepository.save(merchantPayable);

        journalRepository.save(new JournalEntry(order.getId(), nodalEscrow, LedgerEntryType.DEBIT, amount));
        journalRepository.save(new JournalEntry(order.getId(), merchantPayable, LedgerEntryType.CREDIT, amount));
    }
}
"""
    })

    commit("feat(service): add PaymentOrchestratorService executing end-to-end checkout with circuit breaker protection", {
        "backend/src/main/java/com/minipayment/service/PaymentOrchestratorService.java": """package com.minipayment.service;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.enums.PaymentStatus;
import com.minipayment.domain.valueobjects.RouteEvaluationResult;
import com.minipayment.rail.BankRailAdapter;
import com.minipayment.rail.BankRailRegistry;
import com.minipayment.rail.dto.RailTransactionResult;
import com.minipayment.repository.PaymentOrderRepository;
import com.minipayment.resilience.CircuitBreakerRegistryBridge;
import com.minipayment.resilience.RedisSlidingWindowTracker;
import com.minipayment.router.PaymentRouter;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PaymentOrchestratorService {
    private static final Logger log = LoggerFactory.getLogger(PaymentOrchestratorService.class);

    private final PaymentOrderRepository orderRepository;
    private final PaymentRouter router;
    private final BankRailRegistry railRegistry;
    private final CircuitBreakerRegistryBridge circuitBreakerBridge;
    private final RedisSlidingWindowTracker slidingWindowTracker;
    private final LedgerService ledgerService;

    public PaymentOrchestratorService(PaymentOrderRepository orderRepository,
                                     PaymentRouter router,
                                     BankRailRegistry railRegistry,
                                     CircuitBreakerRegistryBridge circuitBreakerBridge,
                                     RedisSlidingWindowTracker slidingWindowTracker,
                                     LedgerService ledgerService) {
        this.orderRepository = orderRepository;
        this.router = router;
        this.railRegistry = railRegistry;
        this.circuitBreakerBridge = circuitBreakerBridge;
        this.slidingWindowTracker = slidingWindowTracker;
        this.ledgerService = ledgerService;
    }

    @Transactional
    public PaymentOrder processPayment(PaymentOrder order) {
        order.setStatus(PaymentStatus.ROUTING);
        RouteEvaluationResult routeDecision = router.selectOptimalRail(order);
        BankRail targetRail = routeDecision.getSelectedRail();
        order.setRoutedRail(targetRail);
        order.incrementAttemptCount();

        BankRailAdapter adapter = railRegistry.getAdapter(targetRail);
        CircuitBreaker cb = circuitBreakerBridge.getCircuitBreaker(targetRail);

        order.setStatus(PaymentStatus.SUBMITTED_TO_PSP);
        long start = System.currentTimeMillis();

        RailTransactionResult railResult;
        try {
            if (cb != null) {
                railResult = cb.executeSupplier(() -> adapter.processPayment(order));
            } else {
                railResult = adapter.processPayment(order);
            }
        } catch (Exception ex) {
            log.error("Circuit breaker exception or timeout calling {}: {}", targetRail, ex.getMessage());
            railResult = RailTransactionResult.failure(targetRail, System.currentTimeMillis() - start, "CB_OPEN_OR_TIMEOUT", ex.getMessage());
        }

        long totalLatency = System.currentTimeMillis() - start;
        order.setLatencyMs(totalLatency);

        // Record metrics in sliding window tracker
        slidingWindowTracker.recordCall(targetRail, railResult.isSuccess(), totalLatency);

        if (railResult.isSuccess()) {
            order.setStatus(PaymentStatus.SUCCESS);
            ledgerService.recordSuccessfulPayment(order);
            log.info("Payment {} SUCCEEDED on rail {} in {}ms", order.getId(), targetRail, totalLatency);
        } else {
            order.setStatus(PaymentStatus.FAILED);
            order.setErrorReason(railResult.getErrorMessage());
            log.warn("Payment {} FAILED on rail {}: {}", order.getId(), targetRail, railResult.getErrorMessage());
        }

        return orderRepository.save(order);
    }
}
"""
    })

    commit("feat(dto): create InitiatePaymentRequest and PaymentResponse API contracts", {
        "backend/src/main/java/com/minipayment/dto/InitiatePaymentRequest.java": """package com.minipayment.dto;

import com.minipayment.domain.enums.Currency;
import com.minipayment.domain.enums.PaymentMethod;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;

public class InitiatePaymentRequest {
    @NotBlank
    private String merchantOrderId;

    @NotNull
    @DecimalMin("1.00")
    private BigDecimal amount;

    @NotNull
    private Currency currency;

    @NotNull
    private PaymentMethod paymentMethod;

    private String customerVpa;

    public InitiatePaymentRequest() {}

    public String getMerchantOrderId() { return merchantOrderId; }
    public void setMerchantOrderId(String merchantOrderId) { this.merchantOrderId = merchantOrderId; }
    public BigDecimal getAmount() { return amount; }
    public void setAmount(BigDecimal amount) { this.amount = amount; }
    public Currency getCurrency() { return currency; }
    public void setCurrency(Currency currency) { this.currency = currency; }
    public PaymentMethod getPaymentMethod() { return paymentMethod; }
    public void setPaymentMethod(PaymentMethod paymentMethod) { this.paymentMethod = paymentMethod; }
    public String getCustomerVpa() { return customerVpa; }
    public void setCustomerVpa(String customerVpa) { this.customerVpa = customerVpa; }
}
""",
        "backend/src/main/java/com/minipayment/dto/PaymentResponse.java": """package com.minipayment.dto;

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
"""
    })

    commit("feat(api): create PaymentController exposing REST endpoints for checkout and status query", {
        "backend/src/main/java/com/minipayment/controller/PaymentController.java": """package com.minipayment.controller;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.dto.InitiatePaymentRequest;
import com.minipayment.dto.PaymentResponse;
import com.minipayment.repository.PaymentOrderRepository;
import com.minipayment.service.PaymentOrchestratorService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/payments")
public class PaymentController {
    private final PaymentOrchestratorService orchestratorService;
    private final PaymentOrderRepository orderRepository;

    public PaymentController(PaymentOrchestratorService orchestratorService, PaymentOrderRepository orderRepository) {
        this.orchestratorService = orchestratorService;
        this.orderRepository = orderRepository;
    }

    @PostMapping
    public ResponseEntity<PaymentResponse> initiatePayment(
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @Valid @RequestBody InitiatePaymentRequest request) {

        String key = (idempotencyKey != null && !idempotencyKey.isBlank()) 
                ? idempotencyKey 
                : UUID.randomUUID().toString();

        Optional<PaymentOrder> existing = orderRepository.findByIdempotencyKey(key);
        if (existing.isPresent()) {
            return ResponseEntity.ok(PaymentResponse.from(existing.get()));
        }

        PaymentOrder order = new PaymentOrder(
                request.getMerchantOrderId(),
                key,
                request.getAmount(),
                request.getCurrency(),
                request.getPaymentMethod()
        );

        PaymentOrder saved = orchestratorService.processPayment(order);
        return ResponseEntity.ok(PaymentResponse.from(saved));
    }

    @GetMapping("/{id}")
    public ResponseEntity<PaymentResponse> getPayment(@PathVariable UUID id) {
        return orderRepository.findById(id)
                .map(order -> ResponseEntity.ok(PaymentResponse.from(order)))
                .orElse(ResponseEntity.notFound().build());
    }
}
"""
    })

    print("Phase 7 complete.")

if __name__ == "__main__":
    run_phase_7()
