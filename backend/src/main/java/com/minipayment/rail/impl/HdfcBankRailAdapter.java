package com.minipayment.rail.impl;

import com.minipayment.domain.enums.BankRail;
import com.minipayment.rail.BaseBankRailAdapter;
import org.springframework.stereotype.Component;

@Component
public class HdfcBankRailAdapter extends BaseBankRailAdapter {
    public HdfcBankRailAdapter() {
        super(BankRail.HDFC_RAIL, 1.45, 110, 40);
    }
}
