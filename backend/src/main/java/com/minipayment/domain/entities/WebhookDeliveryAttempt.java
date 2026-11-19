package com.minipayment.domain.entities;
import jakarta.persistence.*;
import java.util.UUID;
@Entity @Table(name="webhook_delivery_attempts")
public class WebhookDeliveryAttempt extends AuditableEntity { @Id @GeneratedValue private UUID id; }