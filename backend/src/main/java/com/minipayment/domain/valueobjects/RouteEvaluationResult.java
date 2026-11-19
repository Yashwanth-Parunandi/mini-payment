package com.minipayment.domain.valueobjects;

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
