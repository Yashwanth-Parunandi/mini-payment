package com.minipayment.repository;
import com.minipayment.domain.entities.Refund;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;
public interface RefundRepository extends JpaRepository<Refund, UUID> {}