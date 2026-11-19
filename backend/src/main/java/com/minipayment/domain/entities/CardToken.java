package com.minipayment.domain.entities;
import jakarta.persistence.*;
import java.util.UUID;
@Entity @Table(name="card_tokens")
public class CardToken extends AuditableEntity { @Id @GeneratedValue private UUID id; }