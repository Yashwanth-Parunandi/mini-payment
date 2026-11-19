package com.minipayment.domain.entities;
import jakarta.persistence.*;
import java.util.UUID;
@Entity @Table(name="settlement_batches")
public class SettlementBatch extends AuditableEntity { @Id @GeneratedValue private UUID id; }