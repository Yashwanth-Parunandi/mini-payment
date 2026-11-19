package com.minipayment.domain.entities;

import com.minipayment.domain.enums.LedgerEntryType;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "journal_entries")
public class JournalEntry extends AuditableEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "payment_order_id", nullable = false)
    private UUID paymentOrderId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ledger_account_id", nullable = false)
    private LedgerAccount account;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private LedgerEntryType entryType;

    @Column(nullable = false)
    private BigDecimal amount;

    public JournalEntry() {}

    public JournalEntry(UUID paymentOrderId, LedgerAccount account, LedgerEntryType entryType, BigDecimal amount) {
        this.paymentOrderId = paymentOrderId;
        this.account = account;
        this.entryType = entryType;
        this.amount = amount;
    }

    public UUID getId() { return id; }
    public UUID getPaymentOrderId() { return paymentOrderId; }
    public LedgerAccount getAccount() { return account; }
    public LedgerEntryType getEntryType() { return entryType; }
    public BigDecimal getAmount() { return amount; }
}
