package com.minipayment.rail;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.dto.RailTransactionResult;

public interface BankRailAdapter {
    BankRail getRail();
    RailTransactionResult processPayment(PaymentOrder order);
    boolean isHealthy();
    double getCostPercentage();
}
