package com.minipayment.domain.valueobjects;
import java.math.BigDecimal;
public record TransactionFeeSpecification(BigDecimal percentageFee, BigDecimal flatFee) {}