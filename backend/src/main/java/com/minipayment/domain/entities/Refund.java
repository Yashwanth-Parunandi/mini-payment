package com.minipayment.domain.entities;
import jakarta.persistence.*;
import java.util.UUID;
@Entity @Table(name="refunds")
public class Refund extends AuditableEntity { @Id @GeneratedValue private UUID id; }