package com.minipayment.chaos;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.BankRailAdapter;
import com.minipayment.rail.BankRailRegistry;
import com.minipayment.rail.BaseBankRailAdapter;
import com.minipayment.resilience.CircuitBreakerRegistryBridge;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class ChaosSimulatorService {
    private static final Logger log = LoggerFactory.getLogger(ChaosSimulatorService.class);

    private final BankRailRegistry railRegistry;
    private final CircuitBreakerRegistryBridge circuitBreakerBridge;

    public ChaosSimulatorService(BankRailRegistry railRegistry, CircuitBreakerRegistryBridge circuitBreakerBridge) {
        this.railRegistry = railRegistry;
        this.circuitBreakerBridge = circuitBreakerBridge;
    }

    public void applyChaos(ChaosInjectionCommand cmd) {
        BankRailAdapter adapter = railRegistry.getAdapter(cmd.getRail());
        if (adapter instanceof BaseBankRailAdapter base) {
            base.setForcedOutage(cmd.isForcedOutage());
            base.setForcedLatencyMs(cmd.getAdditionalLatencyMs());
            base.setFailureRateOverridePercent(cmd.getFailureRateOverridePercent());

            if (cmd.isForcedOutage()) {
                circuitBreakerBridge.transitionToOpen(cmd.getRail());
                log.warn("CHAOS: Rail {} set to FORCED OUTAGE, Circuit Breaker forcefully tripped OPEN", cmd.getRail());
            } else if (!cmd.isForcedOutage() && circuitBreakerBridge.getState(cmd.getRail()).name().equals("OPEN")) {
                circuitBreakerBridge.transitionToClosed(cmd.getRail());
                log.info("CHAOS: Rail {} restored, Circuit Breaker reset to CLOSED", cmd.getRail());
            }
        }
    }

    public Map<String, Object> getChaosStatus() {
        Map<String, Object> status = new HashMap<>();
        for (BankRail rail : BankRail.values()) {
            BankRailAdapter adapter = railRegistry.getAdapter(rail);
            if (adapter instanceof BaseBankRailAdapter base) {
                Map<String, Object> r = new HashMap<>();
                r.put("forcedOutage", base.isForcedOutage());
                r.put("forcedLatencyMs", base.getForcedLatencyMs());
                r.put("failureRateOverridePercent", base.getFailureRateOverridePercent());
                status.put(rail.name(), r);
            }
        }
        return status;
    }

    public void resetAllChaos() {
        for (BankRail rail : BankRail.values()) {
            BankRailAdapter adapter = railRegistry.getAdapter(rail);
            if (adapter instanceof BaseBankRailAdapter base) {
                base.setForcedOutage(false);
                base.setForcedLatencyMs(0);
                base.setFailureRateOverridePercent(-1);
                circuitBreakerBridge.transitionToClosed(rail);
            }
        }
        log.info("CHAOS: All rails reset to healthy state.");
    }
}
