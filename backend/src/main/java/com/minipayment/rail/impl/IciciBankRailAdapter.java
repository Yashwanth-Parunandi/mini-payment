package com.minipayment.rail.impl;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.BaseBankRailAdapter;
import org.springframework.stereotype.Component;

@Component
public class IciciBankRailAdapter extends BaseBankRailAdapter {
    public IciciBankRailAdapter() {
        super(BankRail.ICICI_RAIL, 1.60, 130, 45);
    }
}
