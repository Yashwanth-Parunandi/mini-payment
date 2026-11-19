package com.minipayment.fraud;
import com.minipayment.domain.entities.PaymentOrder;
public interface RiskEvaluationRule { int evaluate(PaymentOrder order); String ruleName(); }