package com.minipayment.repository;

import com.minipayment.domain.entities.LedgerAccount;
import com.minipayment.domain.enums.AccountType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface LedgerAccountRepository extends JpaRepository<LedgerAccount, UUID> {
    Optional<LedgerAccount> findByAccountNumber(String accountNumber);
    Optional<LedgerAccount> findByAccountType(AccountType accountType);
}
