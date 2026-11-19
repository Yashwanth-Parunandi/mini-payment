package com.minipayment.domain.valueobjects;

import com.minipayment.domain.enums.Currency;
import org.junit.jupiter.api.Test;
import java.math.BigDecimal;
import static org.junit.jupiter.api.Assertions.*;

class MoneyTest {
    @Test
    void testMoneyCreationAndPrecision() {
        Money m = Money.inr(150.256);
        assertEquals(new BigDecimal("150.26"), m.getAmount());
        assertEquals(Currency.INR, m.getCurrency());
    }

    @Test
    void testMoneyAdditionAndSubtraction() {
        Money a = Money.inr(100.50);
        Money b = Money.inr(49.50);
        Money sum = a.add(b);
        assertEquals(new BigDecimal("150.00"), sum.getAmount());

        Money diff = a.subtract(b);
        assertEquals(new BigDecimal("51.00"), diff.getAmount());
    }

    @Test
    void testCurrencyMismatchThrowsException() {
        Money inr = Money.inr(100);
        Money usd = Money.of(100, Currency.USD);
        assertThrows(IllegalArgumentException.class, () -> inr.add(usd));
    }
}
