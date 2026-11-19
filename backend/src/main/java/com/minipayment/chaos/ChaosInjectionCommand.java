package com.minipayment.chaos;

import com.minipayment.domain.enums.BankRail;

public class ChaosInjectionCommand {
    private BankRail rail;
    private boolean forcedOutage;
    private int additionalLatencyMs;
    private int failureRateOverridePercent;

    public BankRail getRail() { return rail; }
    public void setRail(BankRail rail) { this.rail = rail; }
    public boolean isForcedOutage() { return forcedOutage; }
    public void setForcedOutage(boolean forcedOutage) { this.forcedOutage = forcedOutage; }
    public int getAdditionalLatencyMs() { return additionalLatencyMs; }
    public void setAdditionalLatencyMs(int additionalLatencyMs) { this.additionalLatencyMs = additionalLatencyMs; }
    public int getFailureRateOverridePercent() { return failureRateOverridePercent; }
    public void setFailureRateOverridePercent(int failureRateOverridePercent) { this.failureRateOverridePercent = failureRateOverridePercent; }
}
