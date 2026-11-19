package com.minipayment.repository;
import com.minipayment.domain.entities.SettlementBatch;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;
public interface SettlementBatchRepository extends JpaRepository<SettlementBatch, UUID> {}