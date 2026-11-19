package com.minipayment.domain.valueobjects;

import java.io.Serializable;

public class CustomerPaymentProfile implements Serializable {
    private final String customerId;
    private final String vpaAddress;
    private final String maskedCardNumber;
    private final String cardNetwork;

    public CustomerPaymentProfile(String customerId, String vpaAddress, String maskedCardNumber, String cardNetwork) {
        this.customerId = customerId;
        this.vpaAddress = vpaAddress;
        this.maskedCardNumber = maskedCardNumber;
        this.cardNetwork = cardNetwork;
    }

    public static CustomerPaymentProfile forUpi(String customerId, String vpa) {
        return new CustomerPaymentProfile(customerId, vpa, null, null);
    }

    public static CustomerPaymentProfile forCard(String customerId, String maskedCard, String network) {
        return new CustomerPaymentProfile(customerId, null, maskedCard, network);
    }

    public String getCustomerId() { return customerId; }
    public String getVpaAddress() { return vpaAddress; }
    public String getMaskedCardNumber() { return maskedCardNumber; }
    public String getCardNetwork() { return cardNetwork; }
}
