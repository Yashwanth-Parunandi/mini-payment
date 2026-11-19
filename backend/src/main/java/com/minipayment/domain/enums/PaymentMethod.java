package com.minipayment.domain.enums;

public enum PaymentMethod {
    UPI("Unified Payments Interface", true),
    CREDIT_CARD("Credit Card Gateway", false),
    DEBIT_CARD("Debit Card Gateway", false),
    NET_BANKING("NetBanking Portal", true),
    WALLET("Digital Wallet", true);

    private final String displayName;
    private final boolean instantSettlement;

    PaymentMethod(String displayName, boolean instantSettlement) {
        this.displayName = displayName;
        this.instantSettlement = instantSettlement;
    }

    public String getDisplayName() { return displayName; }
    public boolean isInstantSettlement() { return instantSettlement; }
}
