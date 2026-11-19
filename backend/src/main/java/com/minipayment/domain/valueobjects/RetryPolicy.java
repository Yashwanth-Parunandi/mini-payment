package com.minipayment.domain.valueobjects;
public record RetryPolicy(int maxRetries, long initialDelayMs, double backoffMultiplier) {}