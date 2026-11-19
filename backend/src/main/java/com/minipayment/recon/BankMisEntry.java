package com.minipayment.recon;
import java.math.BigDecimal;
import java.time.Instant;
public record BankMisEntry(String bankRef, String orderId, BigDecimal amount, Instant timestamp) {}