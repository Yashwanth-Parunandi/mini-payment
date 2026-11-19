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

def run_phase_6():
    print("--- Running Phase 6: Dynamic Smart Routing Engine ---")

    commit("feat(router): define PaymentRouter interface for intelligent rail selection", {
        "backend/src/main/java/com/minipayment/router/PaymentRouter.java": """package com.minipayment.router;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.valueobjects.RouteEvaluationResult;

public interface PaymentRouter {
    RouteEvaluationResult selectOptimalRail(PaymentOrder order);
}
"""
    })

    commit("feat(router): implement SmartDynamicPaymentRouter evaluating health, latency and cost weights", {
        "backend/src/main/java/com/minipayment/router/impl/SmartDynamicPaymentRouter.java": """package com.minipayment.router.impl;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.enums.CircuitBreakerState;
import com.minipayment.domain.valueobjects.RouteEvaluationResult;
import com.minipayment.rail.BankRailAdapter;
import com.minipayment.rail.BankRailRegistry;
import com.minipayment.resilience.CircuitBreakerRegistryBridge;
import com.minipayment.resilience.RedisSlidingWindowTracker;
import com.minipayment.router.PaymentRouter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class SmartDynamicPaymentRouter implements PaymentRouter {
    private static final Logger log = LoggerFactory.getLogger(SmartDynamicPaymentRouter.class);

    private static final double WEIGHT_SUCCESS_RATE = 0.60;
    private static final double WEIGHT_LATENCY = 0.25;
    private static final double WEIGHT_COST = 0.15;
    private static final long MAX_LATENCY_CEILING_MS = 3000;

    private final BankRailRegistry railRegistry;
    private final RedisSlidingWindowTracker slidingWindowTracker;
    private final CircuitBreakerRegistryBridge circuitBreakerBridge;

    public SmartDynamicPaymentRouter(BankRailRegistry railRegistry,
                                     RedisSlidingWindowTracker slidingWindowTracker,
                                     CircuitBreakerRegistryBridge circuitBreakerBridge) {
        this.railRegistry = railRegistry;
        this.slidingWindowTracker = slidingWindowTracker;
        this.circuitBreakerBridge = circuitBreakerBridge;
    }

    @Override
    public RouteEvaluationResult selectOptimalRail(PaymentOrder order) {
        List<BankRail> candidateRails = Arrays.asList(BankRail.values());
        
        BankRail bestRail = null;
        double highestScore = -1.0;
        double bestSuccessRate = 0.0;
        long bestP90 = 0;
        CircuitBreakerState bestCbState = CircuitBreakerState.CLOSED;
        StringBuilder explanation = new StringBuilder();

        for (BankRail rail : candidateRails) {
            CircuitBreakerState cbState = circuitBreakerBridge.getState(rail);
            
            // Skip OPEN circuit breaker rails to prevent cascading downtime
            if (cbState == CircuitBreakerState.OPEN) {
                explanation.append("[").append(rail.name()).append(": REJECTED (Circuit OPEN)] ");
                continue;
            }

            double successRate = slidingWindowTracker.getSuccessRate(rail);
            long p90Latency = slidingWindowTracker.getP90LatencyMs(rail);
            BankRailAdapter adapter = railRegistry.getAdapter(rail);
            double cost = adapter.getCostPercentage();

            // Calculate composite dynamic score
            double successPart = (successRate / 100.0) * (WEIGHT_SUCCESS_RATE * 100.0);
            double latencyNorm = Math.max(0, (double)(MAX_LATENCY_CEILING_MS - p90Latency) / MAX_LATENCY_CEILING_MS);
            double latencyPart = latencyNorm * (WEIGHT_LATENCY * 100.0);
            double costPart = (1.0 - (cost / 3.0)) * (WEIGHT_COST * 100.0);

            double compositeScore = successPart + latencyPart + costPart;
            if (cbState == CircuitBreakerState.HALF_OPEN) {
                compositeScore *= 0.5; // Dampen traffic in half-open trial
            }

            explanation.append(String.format("[%s: score=%.1f (SR=%.0f%%, Lat=%dms)] ", 
                    rail.name(), compositeScore, successRate, p90Latency));

            if (compositeScore > highestScore) {
                highestScore = compositeScore;
                bestRail = rail;
                bestSuccessRate = successRate;
                bestP90 = p90Latency;
                bestCbState = cbState;
            }
        }

        // Fallback safety if all primary circuits are down
        if (bestRail == null) {
            log.warn("CRITICAL: All bank circuits are OPEN. Engaging emergency failover rail Axis UPI");
            bestRail = BankRail.AXIS_UPI_RAIL;
            explanation.append("-> FORCED EMERGENCY FAILOVER TO AXIS_UPI");
        }

        log.info("Smart Router selected {} (score={}) for order {}", bestRail, highestScore, order.getMerchantOrderId());
        return new RouteEvaluationResult(bestRail, highestScore, bestSuccessRate, bestP90, bestCbState, explanation.toString());
    }
}
"""
    })

    print("Phase 6 complete.")

if __name__ == "__main__":
    run_phase_6()
