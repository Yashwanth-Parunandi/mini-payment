package com.minipayment.repository;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.enums.PaymentStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface PaymentOrderRepository extends JpaRepository<PaymentOrder, UUID> {
    Optional<PaymentOrder> findByIdempotencyKey(String idempotencyKey);
    List<PaymentOrder> findByStatus(PaymentStatus status);
    Page<PaymentOrder> findByRoutedRail(BankRail routedRail, Pageable pageable);
    long countByRoutedRailAndStatus(BankRail rail, PaymentStatus status);
}
