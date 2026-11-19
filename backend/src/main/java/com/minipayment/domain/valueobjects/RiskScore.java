package com.minipayment.domain.valueobjects;
public record RiskScore(int score, boolean approved, String reason) {}