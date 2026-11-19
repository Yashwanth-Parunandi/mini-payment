package com.minipayment.rail;

import com.minipayment.domain.enums.BankRail;
import org.springframework.stereotype.Component;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

@Component
public class BankRailRegistry {
    private final Map<BankRail, BankRailAdapter> adapterMap;

    public BankRailRegistry(List<BankRailAdapter> adapters) {
        this.adapterMap = adapters.stream()
                .collect(Collectors.toMap(BankRailAdapter::getRail, Function.identity()));
    }

    public BankRailAdapter getAdapter(BankRail rail) {
        BankRailAdapter adapter = adapterMap.get(rail);
        if (adapter == null) {
            throw new IllegalArgumentException("No rail adapter registered for: " + rail);
        }
        return adapter;
    }

    public Collection<BankRailAdapter> getAllAdapters() {
        return Collections.unmodifiableCollection(adapterMap.values());
    }
}
