package com.minipayment.domain.entities;
import jakarta.persistence.*;
import java.util.UUID;
@Entity @Table(name="merchant_tier_limits")
public class MerchantTierLimit extends AuditableEntity { @Id @GeneratedValue private UUID id; }