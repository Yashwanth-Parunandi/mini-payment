package com.minipayment.repository;
import com.minipayment.domain.entities.Chargeback;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;
public interface ChargebackRepository extends JpaRepository<Chargeback, UUID> {}