package com.minipayment.domain.entities;

import com.minipayment.domain.enums.AccountType;
import com.minipayment.domain.enums.Currency;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "ledger_accounts")
public class LedgerAccount extends AuditableEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "account_number", nullable = false, unique = true)
    private String accountNumber;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AccountType accountType;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Currency currency;

    @Column(nullable = false)
    private BigDecimal currentBalance = BigDecimal.ZERO;

    public LedgerAccount() {}

    public LedgerAccount(String accountNumber, AccountType accountType, Currency currency) {
        this.accountNumber = accountNumber;
        this.accountType = accountType;
        this.currency = currency;
        this.currentBalance = BigDecimal.ZERO;
    }

    public UUID getId() { return id; }
    public String getAccountNumber() { return accountNumber; }
    public AccountType getAccountType() { return accountType; }
    public Currency getCurrency() { return currency; }
    public BigDecimal getCurrentBalance() { return currentBalance; }
    public void setCurrentBalance(BigDecimal currentBalance) { this.currentBalance = currentBalance; }
}
