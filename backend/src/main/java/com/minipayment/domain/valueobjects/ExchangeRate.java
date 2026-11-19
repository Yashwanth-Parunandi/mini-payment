package com.minipayment.domain.valueobjects;
import java.math.BigDecimal;
import com.minipayment.domain.enums.Currency;
public record ExchangeRate(Currency source, Currency target, BigDecimal rate) {}