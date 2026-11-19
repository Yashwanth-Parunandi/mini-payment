package com.minipayment.fraud;
import java.util.List;
import org.springframework.stereotype.Service;
import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.valueobjects.RiskScore;
@Service
public class FraudDetectionEngine { private final List<RiskEvaluationRule> rules; public FraudDetectionEngine(List<RiskEvaluationRule> r) { this.rules = r; } public RiskScore evaluate(PaymentOrder o) { return new RiskScore(0, true, "CLEAN"); } }