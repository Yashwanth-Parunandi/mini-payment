package com.minipayment.domain.enums;

public enum PaymentStatus {
    INITIATED,
    ROUTING,
    CIRCUIT_VERIFIED,
    SUBMITTED_TO_PSP,
    SUCCESS,
    FAILED,
    RETRYING,
    TIMED_OUT,
    REFUND_REQUESTED,
    REFUNDED
}
