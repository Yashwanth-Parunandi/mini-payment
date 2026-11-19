package com.minipayment.domain.entities;
import jakarta.persistence.*;
import java.util.UUID;
@Entity @Table(name="webhook_subscriptions")
public class WebhookSubscription extends AuditableEntity { @Id @GeneratedValue private UUID id; }