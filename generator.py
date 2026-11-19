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

def run_phase_4():
    print("--- Running Phase 4: Simulated PSP Rail Adapters ---")

    commit("feat(rail): define BankRailAdapter SPI interface for payment execution", {
        "backend/src/main/java/com/minipayment/rail/BankRailAdapter.java": """package com.minipayment.rail;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.dto.RailTransactionResult;

public interface BankRailAdapter {
    BankRail getRail();
    RailTransactionResult processPayment(PaymentOrder order);
    boolean isHealthy();
    double getCostPercentage();
}
"""
    })

    commit("feat(rail): create RailTransactionResult DTO for response payload", {
        "backend/src/main/java/com/minipayment/rail/dto/RailTransactionResult.java": """package com.minipayment.rail.dto;

import com.minipayment.domain.enums.BankRail;
import java.io.Serializable;
import java.time.Instant;

public class RailTransactionResult implements Serializable {
    private final boolean success;
    private final String pspReferenceId;
    private final BankRail rail;
    private final long latencyMs;
    private final String errorCode;
    private final String errorMessage;
    private final Instant processedAt;

    public RailTransactionResult(boolean success, String pspReferenceId, BankRail rail, 
                                 long latencyMs, String errorCode, String errorMessage) {
        this.success = success;
        this.pspReferenceId = pspReferenceId;
        this.rail = rail;
        this.latencyMs = latencyMs;
        this.errorCode = errorCode;
        this.errorMessage = errorMessage;
        this.processedAt = Instant.now();
    }

    public static RailTransactionResult success(String pspReferenceId, BankRail rail, long latencyMs) {
        return new RailTransactionResult(true, pspReferenceId, rail, latencyMs, null, null);
    }

    public static RailTransactionResult failure(BankRail rail, long latencyMs, String errorCode, String errorMessage) {
        return new RailTransactionResult(false, null, rail, latencyMs, errorCode, errorMessage);
    }

    public boolean isSuccess() { return success; }
    public String getPspReferenceId() { return pspReferenceId; }
    public BankRail getRail() { return rail; }
    public long getLatencyMs() { return latencyMs; }
    public String getErrorCode() { return errorCode; }
    public String getErrorMessage() { return errorMessage; }
    public Instant getProcessedAt() { return processedAt; }
}
"""
    })

    commit("feat(rail): add BaseBankRailAdapter abstract class handling chaos injection and latency simulation", {
        "backend/src/main/java/com/minipayment/rail/BaseBankRailAdapter.java": """package com.minipayment.rail;

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
"""
    })

    commit("feat(rail): implement HdfcBankRailAdapter with SmartGateway specifications", {
        "backend/src/main/java/com/minipayment/rail/impl/HdfcBankRailAdapter.java": """package com.minipayment.rail.impl;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.BaseBankRailAdapter;
import org.springframework.stereotype.Component;

@Component
public class HdfcBankRailAdapter extends BaseBankRailAdapter {
    public HdfcBankRailAdapter() {
        super(BankRail.HDFC_RAIL, 1.45, 110, 40);
    }
}
"""
    })

    commit("feat(rail): implement IciciBankRailAdapter with Corporate Rail specifications", {
        "backend/src/main/java/com/minipayment/rail/impl/IciciBankRailAdapter.java": """package com.minipayment.rail.impl;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.BaseBankRailAdapter;
import org.springframework.stereotype.Component;

@Component
public class IciciBankRailAdapter extends BaseBankRailAdapter {
    public IciciBankRailAdapter() {
        super(BankRail.ICICI_RAIL, 1.60, 130, 45);
    }
}
"""
    })

    commit("feat(rail): implement SbiBankRailAdapter with National Payment Rail specifications", {
        "backend/src/main/java/com/minipayment/rail/impl/SbiBankRailAdapter.java": """package com.minipayment.rail.impl;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.BaseBankRailAdapter;
import org.springframework.stereotype.Component;

@Component
public class SbiBankRailAdapter extends BaseBankRailAdapter {
    public SbiBankRailAdapter() {
        super(BankRail.SBI_RAIL, 1.10, 190, 80);
    }
}
"""
    })

    commit("feat(rail): implement AxisUpiRailAdapter with Instant UPI Rail specifications", {
        "backend/src/main/java/com/minipayment/rail/impl/AxisUpiRailAdapter.java": """package com.minipayment.rail.impl;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.BaseBankRailAdapter;
import org.springframework.stereotype.Component;

@Component
public class AxisUpiRailAdapter extends BaseBankRailAdapter {
    public AxisUpiRailAdapter() {
        super(BankRail.AXIS_UPI_RAIL, 0.85, 80, 25);
    }
}
"""
    })

    commit("feat(rail): add BankRailRegistry managing adapter discovery and lookup", {
        "backend/src/main/java/com/minipayment/rail/BankRailRegistry.java": """package com.minipayment.rail;

import com.minipayment.domain.enums.BankRail;
import org.springframework.stereotype.Component;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

@Component
public class BankRailRegistry {
    private final Map<BankRail, BankRailAdapter> adapterMap;

    public BankRailRegistry(List<BankRailAdapter> adapters) {
        this.adapterMap = adapters.stream()
                .collect(Collectors.toMap(BankRailAdapter::getRail, Function.identity()));
    }

    public BankRailAdapter getAdapter(BankRail rail) {
        BankRailAdapter adapter = adapterMap.get(rail);
        if (adapter == null) {
            throw new IllegalArgumentException("No rail adapter registered for: " + rail);
        }
        return adapter;
    }

    public Collection<BankRailAdapter> getAllAdapters() {
        return Collections.unmodifiableCollection(adapterMap.values());
    }
}
"""
    })

    print("Phase 4 complete.")

if __name__ == "__main__":
    run_phase_4()
