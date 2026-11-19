package com.minipayment.service;

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
