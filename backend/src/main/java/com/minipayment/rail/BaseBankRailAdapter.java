package com.minipayment.rail;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.dto.RailTransactionResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

public abstract class BaseBankRailAdapter implements BankRailAdapter {
    protected final Logger log = LoggerFactory.getLogger(getClass());

    protected final BankRail rail;
    protected final double costPercentage;
    protected final int baselineLatencyMs;
    protected final int jitterRangeMs;

    // Chaos injection fields
    protected final AtomicBoolean forcedOutage = new AtomicBoolean(false);
    protected final AtomicInteger forcedLatencyMs = new AtomicInteger(0);
    protected final AtomicInteger failureRateOverridePercent = new AtomicInteger(-1);

    public BaseBankRailAdapter(BankRail rail, double costPercentage, int baselineLatencyMs, int jitterRangeMs) {
        this.rail = rail;
        this.costPercentage = costPercentage;
        this.baselineLatencyMs = baselineLatencyMs;
        this.jitterRangeMs = jitterRangeMs;
    }

    @Override
    public BankRail getRail() { return rail; }

    @Override
    public double getCostPercentage() { return costPercentage; }

    @Override
    public boolean isHealthy() { return !forcedOutage.get(); }

    public void setForcedOutage(boolean outage) {
        this.forcedOutage.set(outage);
        log.warn("Chaos injection updated for {}: forcedOutage={}", rail, outage);
    }

    public void setForcedLatencyMs(int latencyMs) {
        this.forcedLatencyMs.set(latencyMs);
    }

    public void setFailureRateOverridePercent(int percent) {
        this.failureRateOverridePercent.set(percent);
    }

    public boolean isForcedOutage() { return forcedOutage.get(); }
    public int getForcedLatencyMs() { return forcedLatencyMs.get(); }
    public int getFailureRateOverridePercent() { return failureRateOverridePercent.get(); }

    @Override
    public RailTransactionResult processPayment(PaymentOrder order) {
        long startTime = System.currentTimeMillis();

        // Calculate simulated latency
        int totalSleep = baselineLatencyMs + ThreadLocalRandom.current().nextInt(0, jitterRangeMs + 1) + forcedLatencyMs.get();
        try {
            Thread.sleep(Math.min(totalSleep, 15000));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        long actualLatency = System.currentTimeMillis() - startTime;

        // Check forced outage
        if (forcedOutage.get()) {
            log.error("Rail {} rejected transaction {} due to active chaos outage", rail, order.getId());
            return RailTransactionResult.failure(rail, actualLatency, "BANK_GATEWAY_OUTAGE_503", "Bank connection dropped / Service Unavailable");
        }

        // Check simulated failure override
        int override = failureRateOverridePercent.get();
        if (override >= 0) {
            int roll = ThreadLocalRandom.current().nextInt(100);
            if (roll < override) {
                return RailTransactionResult.failure(rail, actualLatency, "SIMULATED_FAILOVER_SPIKE", "High transient rejection rate detected at bank node");
            }
        }

        // Normal base failure rate (1% to 2% realistic network noise)
        if (ThreadLocalRandom.current().nextInt(100) < 2) {
            return RailTransactionResult.failure(rail, actualLatency, "TRANSIENT_NETWORK_TIMEOUT", "Bank SMS OTP rail / authorization timed out");
        }

        String pspRef = rail.getCode() + "_" + UUID.randomUUID().toString().substring(0, 12).toUpperCase();
        return RailTransactionResult.success(pspRef, rail, actualLatency);
    }
}
