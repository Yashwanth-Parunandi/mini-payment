package com.minipayment.domain.enums;

public enum BankRail {
    HDFC_RAIL("HDFC Bank SmartGateway", "HDFC_01", 120),
    ICICI_RAIL("ICICI Bank Corporate Rail", "ICICI_01", 140),
    SBI_RAIL("State Bank of India Core Rail", "SBI_01", 210),
    AXIS_UPI_RAIL("Axis Bank Instant UPI Rail", "AXIS_01", 90);

    private final String gatewayName;
    private final String code;
    private final int baselineLatencyMs;

    BankRail(String gatewayName, String code, int baselineLatencyMs) {
        this.gatewayName = gatewayName;
        this.code = code;
        this.baselineLatencyMs = baselineLatencyMs;
    }

    public String getGatewayName() { return gatewayName; }
    public String getCode() { return code; }
    public int getBaselineLatencyMs() { return baselineLatencyMs; }
}
