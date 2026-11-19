package com.minipayment.resilience;

import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import io.github.resilience4j.circuitbreaker.event.CircuitBreakerOnStateTransitionEvent;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Component;

@Component
public class CircuitBreakerEventListener {
    private static final Logger log = LoggerFactory.getLogger(CircuitBreakerEventListener.class);

    private final CircuitBreakerRegistry circuitBreakerRegistry;
    private final ApplicationEventPublisher eventPublisher;

    public CircuitBreakerEventListener(CircuitBreakerRegistry circuitBreakerRegistry, ApplicationEventPublisher eventPublisher) {
        this.circuitBreakerRegistry = circuitBreakerRegistry;
        this.eventPublisher = eventPublisher;
    }

    @PostConstruct
    public void registerListeners() {
        circuitBreakerRegistry.getAllCircuitBreakers().forEach(cb -> {
            cb.getEventPublisher().onStateTransition(this::handleStateTransition);
        });
    }

    private void handleStateTransition(CircuitBreakerOnStateTransitionEvent event) {
        log.warn("CIRCUIT BREAKER STATE CHANGE: '{}' transitioned from {} to {}",
                event.getCircuitBreakerName(),
                event.getStateTransition().getFromState(),
                event.getStateTransition().getToState());
        eventPublisher.publishEvent(event);
    }
}
