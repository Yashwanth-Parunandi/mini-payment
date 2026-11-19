package com.minipayment.router.strategy;
import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.entities.PaymentOrder;
import java.util.List;
public interface RoutingStrategy { BankRail route(PaymentOrder order, List<BankRail> candidates); }