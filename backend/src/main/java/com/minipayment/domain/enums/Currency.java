package com.minipayment.domain.enums;

public enum Currency {
    INR("Indian Rupee", 2),
    USD("US Dollar", 2),
    EUR("Euro", 2),
    GBP("British Pound", 2),
    SGD("Singapore Dollar", 2);

    private final String description;
    private final int minorUnitFraction;

    Currency(String description, int minorUnitFraction) {
        this.description = description;
        this.minorUnitFraction = minorUnitFraction;
    }

    public String getDescription() { return description; }
    public int getMinorUnitFraction() { return minorUnitFraction; }
}
