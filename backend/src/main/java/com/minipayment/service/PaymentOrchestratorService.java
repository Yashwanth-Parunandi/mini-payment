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
        PaymentOrder persistedOrder = orderRepository.save(order);

        RouteEvaluationResult routeDecision = router.selectOptimalRail(persistedOrder);
        BankRail targetRail = routeDecision.getSelectedRail();
        persistedOrder.setRoutedRail(targetRail);
        persistedOrder.incrementAttemptCount();

        BankRailAdapter adapter = railRegistry.getAdapter(targetRail);
        CircuitBreaker cb = circuitBreakerBridge.getCircuitBreaker(targetRail);

        persistedOrder.setStatus(PaymentStatus.SUBMITTED_TO_PSP);
        long start = System.currentTimeMillis();

        RailTransactionResult railResult;
        try {
            if (cb != null) {
                railResult = cb.executeSupplier(() -> adapter.processPayment(persistedOrder));
            } else {
                railResult = adapter.processPayment(persistedOrder);
            }
        } catch (Exception ex) {
            log.error("Circuit breaker exception or timeout calling {}: {}", targetRail, ex.getMessage());
            railResult = RailTransactionResult.failure(targetRail, System.currentTimeMillis() - start, "CB_OPEN_OR_TIMEOUT", ex.getMessage());
        }

        long totalLatency = System.currentTimeMillis() - start;
        persistedOrder.setLatencyMs(totalLatency);

        // Record metrics in sliding window tracker
        slidingWindowTracker.recordCall(targetRail, railResult.isSuccess(), totalLatency);

        // IN-FLIGHT AUTO-FAILOVER: If primary attempt failed, immediately retry on secondary healthy rail
        if (!railResult.isSuccess()) {
            BankRail fallbackRail = (targetRail == BankRail.AXIS_UPI_RAIL) ? BankRail.ICICI_RAIL : BankRail.AXIS_UPI_RAIL;
            log.warn("Auto-failover engaged: Rail {} failed, attempting immediate in-flight reroute to {}", targetRail, fallbackRail);
            
            BankRailAdapter fallbackAdapter = railRegistry.getAdapter(fallbackRail);
            CircuitBreaker fallbackCb = circuitBreakerBridge.getCircuitBreaker(fallbackRail);
            persistedOrder.setRoutedRail(fallbackRail);
            persistedOrder.incrementAttemptCount();

            long fallbackStart = System.currentTimeMillis();
            try {
                if (fallbackCb != null) {
                    railResult = fallbackCb.executeSupplier(() -> fallbackAdapter.processPayment(persistedOrder));
                } else {
                    railResult = fallbackAdapter.processPayment(persistedOrder);
                }
            } catch (Exception ex) {
                railResult = RailTransactionResult.failure(fallbackRail, System.currentTimeMillis() - fallbackStart, "FALLBACK_TIMEOUT", ex.getMessage());
            }

            long fallbackLatency = System.currentTimeMillis() - fallbackStart;
            slidingWindowTracker.recordCall(fallbackRail, railResult.isSuccess(), fallbackLatency);
            persistedOrder.setLatencyMs(totalLatency + fallbackLatency);
        }

        if (railResult.isSuccess()) {
            persistedOrder.setStatus(PaymentStatus.SUCCESS);
            ledgerService.recordSuccessfulPayment(persistedOrder);
            log.info("Payment {} SUCCEEDED on rail {} in {}ms", persistedOrder.getId(), persistedOrder.getRoutedRail(), persistedOrder.getLatencyMs());
        } else {
            persistedOrder.setStatus(PaymentStatus.FAILED);
            persistedOrder.setErrorReason(railResult.getErrorMessage());
            log.warn("Payment {} FAILED on rail {}: {}", persistedOrder.getId(), persistedOrder.getRoutedRail(), railResult.getErrorMessage());
        }

        return orderRepository.save(persistedOrder);
    }
}
