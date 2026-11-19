package com.minipayment.domain.valueobjects;
import java.util.Set;
import com.minipayment.domain.enums.PaymentMethod;
public record RailCapabilities(Set<PaymentMethod> supportedMethods, boolean allowsRefunds) {}