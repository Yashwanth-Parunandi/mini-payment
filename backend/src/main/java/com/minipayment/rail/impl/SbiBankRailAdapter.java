package com.minipayment.rail.impl;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.BaseBankRailAdapter;
import org.springframework.stereotype.Component;

@Component
public class SbiBankRailAdapter extends BaseBankRailAdapter {
    public SbiBankRailAdapter() {
        super(BankRail.SBI_RAIL, 1.10, 190, 80);
    }
}
