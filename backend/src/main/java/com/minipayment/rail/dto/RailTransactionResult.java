package com.minipayment.rail.dto;

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
