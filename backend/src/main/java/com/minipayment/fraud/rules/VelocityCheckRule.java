package com.minipayment.fraud.rules;
import com.minipayment.fraud.RiskEvaluationRule;
import com.minipayment.domain.entities.PaymentOrder;
import org.springframework.stereotype.Component;
@Component
public class VelocityCheckRule implements RiskEvaluationRule { public int evaluate(PaymentOrder o) { return 0; } public String ruleName() { return "VELOCITY_CHECK"; } }