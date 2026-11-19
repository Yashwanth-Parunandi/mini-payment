package com.minipayment.router;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.valueobjects.RouteEvaluationResult;

public interface PaymentRouter {
    RouteEvaluationResult selectOptimalRail(PaymentOrder order);
}
