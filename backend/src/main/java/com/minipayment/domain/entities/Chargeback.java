package com.minipayment.domain.entities;
import jakarta.persistence.*;
import java.util.UUID;
@Entity @Table(name="chargebacks")
public class Chargeback extends AuditableEntity { @Id @GeneratedValue private UUID id; }