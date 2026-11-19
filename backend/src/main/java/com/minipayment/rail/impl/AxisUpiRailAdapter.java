package com.minipayment.rail.impl;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.BaseBankRailAdapter;
import org.springframework.stereotype.Component;

@Component
public class AxisUpiRailAdapter extends BaseBankRailAdapter {
    public AxisUpiRailAdapter() {
        super(BankRail.AXIS_UPI_RAIL, 0.85, 80, 25);
    }
}
