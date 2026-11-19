package com.minipayment.domain.entities;
import jakarta.persistence.*;
import java.util.UUID;
@Entity @Table(name="audit_log_events")
public class AuditLogEvent extends AuditableEntity { @Id @GeneratedValue private UUID id; }