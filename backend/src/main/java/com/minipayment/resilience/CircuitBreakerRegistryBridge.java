package com.minipayment.resilience;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.enums.CircuitBreakerState;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class CircuitBreakerRegistryBridge {
    private final CircuitBreakerRegistry circuitBreakerRegistry;
    private final Map<BankRail, CircuitBreaker> railCircuitBreakerMap = new ConcurrentHashMap<>();

    public CircuitBreakerRegistryBridge(CircuitBreakerRegistry circuitBreakerRegistry) {
        this.circuitBreakerRegistry = circuitBreakerRegistry;
        registerRail(BankRail.HDFC_RAIL, "hdfc-rail");
        registerRail(BankRail.ICICI_RAIL, "icici-rail");
        registerRail(BankRail.SBI_RAIL, "sbi-rail");
        registerRail(BankRail.AXIS_UPI_RAIL, "axis-rail");
    }

    private void registerRail(BankRail rail, String configName) {
        CircuitBreaker cb = circuitBreakerRegistry.circuitBreaker(configName);
        railCircuitBreakerMap.put(rail, cb);
    }

    public CircuitBreaker getCircuitBreaker(BankRail rail) {
        return railCircuitBreakerMap.get(rail);
    }

    public CircuitBreakerState getState(BankRail rail) {
        CircuitBreaker cb = railCircuitBreakerMap.get(rail);
        if (cb == null) return CircuitBreakerState.CLOSED;

        CircuitBreaker.State state = cb.getState();
        return switch (state) {
            case OPEN, FORCED_OPEN -> CircuitBreakerState.OPEN;
            case HALF_OPEN -> CircuitBreakerState.HALF_OPEN;
            default -> CircuitBreakerState.CLOSED;
        };
    }

    public void transitionToOpen(BankRail rail) {
        CircuitBreaker cb = railCircuitBreakerMap.get(rail);
        if (cb != null) {
            cb.transitionToOpenState();
        }
    }

    public void transitionToClosed(BankRail rail) {
        CircuitBreaker cb = railCircuitBreakerMap.get(rail);
        if (cb != null) {
            cb.transitionToClosedState();
        }
    }
}
