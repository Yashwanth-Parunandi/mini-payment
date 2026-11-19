package com.minipayment.service;

import com.minipayment.domain.entities.JournalEntry;
import com.minipayment.domain.entities.LedgerAccount;
import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.enums.AccountType;
import com.minipayment.domain.enums.LedgerEntryType;
import com.minipayment.repository.JournalEntryRepository;
import com.minipayment.repository.LedgerAccountRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

@Service
public class LedgerService {
    private final LedgerAccountRepository accountRepository;
    private final JournalEntryRepository journalRepository;

    public LedgerService(LedgerAccountRepository accountRepository, JournalEntryRepository journalRepository) {
        this.accountRepository = accountRepository;
        this.journalRepository = journalRepository;
    }

    @Transactional
    public void recordSuccessfulPayment(PaymentOrder order) {
        LedgerAccount nodalEscrow = accountRepository.findByAccountType(AccountType.NODAL_ESCROW)
                .orElseGet(() -> {
                    LedgerAccount acc = new LedgerAccount("ESCROW_NODAL_INR_01", AccountType.NODAL_ESCROW, order.getCurrency());
                    acc.setCurrentBalance(new BigDecimal("10000000.00"));
                    return accountRepository.save(acc);
                });
        
        LedgerAccount merchantPayable = accountRepository.findByAccountType(AccountType.MERCHANT_PAYABLE)
                .orElseGet(() -> {
                    LedgerAccount acc = new LedgerAccount("MERCHANT_GENERIC_01", AccountType.MERCHANT_PAYABLE, order.getCurrency());
                    return accountRepository.save(acc);
                });

        BigDecimal amount = order.getAmount();

        // Double-entry: Debit Escrow (+ asset), Credit Merchant Payable (+ liability)
        nodalEscrow.setCurrentBalance(nodalEscrow.getCurrentBalance().add(amount));
        merchantPayable.setCurrentBalance(merchantPayable.getCurrentBalance().add(amount));

        accountRepository.save(nodalEscrow);
        accountRepository.save(merchantPayable);

        journalRepository.save(new JournalEntry(order.getId(), nodalEscrow, LedgerEntryType.DEBIT, amount));
        journalRepository.save(new JournalEntry(order.getId(), merchantPayable, LedgerEntryType.CREDIT, amount));
    }
}
