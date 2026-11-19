package com.minipayment.repository;
import com.minipayment.domain.entities.AuditLogEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;
public interface AuditLogEventRepository extends JpaRepository<AuditLogEvent, UUID> {}