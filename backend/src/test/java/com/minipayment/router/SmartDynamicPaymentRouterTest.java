package com.minipayment.router;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.enums.CircuitBreakerState;
import com.minipayment.domain.enums.Currency;
import com.minipayment.domain.enums.PaymentMethod;
import com.minipayment.domain.valueobjects.RouteEvaluationResult;
import com.minipayment.rail.BankRailRegistry;
import com.minipayment.rail.impl.AxisUpiRailAdapter;
import com.minipayment.rail.impl.HdfcBankRailAdapter;
import com.minipayment.rail.impl.IciciBankRailAdapter;
import com.minipayment.rail.impl.SbiBankRailAdapter;
import com.minipayment.resilience.CircuitBreakerRegistryBridge;
import com.minipayment.resilience.RedisSlidingWindowTracker;
import com.minipayment.router.impl.SmartDynamicPaymentRouter;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.math.BigDecimal;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

class SmartDynamicPaymentRouterTest {
    private CircuitBreakerRegistryBridge cbBridge;
    private RedisSlidingWindowTracker slidingWindow;
    private SmartDynamicPaymentRouter router;

    @BeforeEach
    void setUp() {
        cbBridge = Mockito.mock(CircuitBreakerRegistryBridge.class);
        slidingWindow = Mockito.mock(RedisSlidingWindowTracker.class);
        BankRailRegistry registry = new BankRailRegistry(List.of(
                new HdfcBankRailAdapter(),
                new IciciBankRailAdapter(),
                new SbiBankRailAdapter(),
                new AxisUpiRailAdapter()
        ));
        router = new SmartDynamicPaymentRouter(registry, slidingWindow, cbBridge);
    }

    @Test
    void testFailoverWhenPrimaryRailCircuitIsOpen() {
        // HDFC Circuit is OPEN (down)
        when(cbBridge.getState(BankRail.HDFC_RAIL)).thenReturn(CircuitBreakerState.OPEN);
        when(cbBridge.getState(BankRail.ICICI_RAIL)).thenReturn(CircuitBreakerState.CLOSED);
        when(cbBridge.getState(BankRail.SBI_RAIL)).thenReturn(CircuitBreakerState.CLOSED);
        when(cbBridge.getState(BankRail.AXIS_UPI_RAIL)).thenReturn(CircuitBreakerState.CLOSED);

        when(slidingWindow.getSuccessRate(BankRail.AXIS_UPI_RAIL)).thenReturn(99.0);
        when(slidingWindow.getP90LatencyMs(BankRail.AXIS_UPI_RAIL)).thenReturn(85L);

        PaymentOrder order = new PaymentOrder("ORD-001", "KEY-1", BigDecimal.valueOf(500), Currency.INR, PaymentMethod.UPI);
        RouteEvaluationResult decision = router.selectOptimalRail(order);

        assertNotEquals(BankRail.HDFC_RAIL, decision.getSelectedRail());
        assertTrue(decision.getSelectedRail() == BankRail.AXIS_UPI_RAIL || decision.getSelectedRail() == BankRail.ICICI_RAIL);
    }
}
