package com.minipayment.domain.entities;

import jakarta.persistence.*;
import java.util.UUID;

@Entity
@Table(name = "merchants")
public class Merchant extends AuditableEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, unique = true)
    private String apiKey;

    @Column(nullable = false)
    private String businessName;

    @Column(nullable = false)
    private String webhookUrl;

    @Column(nullable = false)
    private boolean active = true;

    public Merchant() {}

    public Merchant(String businessName, String apiKey, String webhookUrl) {
        this.businessName = businessName;
        this.apiKey = apiKey;
        this.webhookUrl = webhookUrl;
    }

    public UUID getId() { return id; }
    public String getApiKey() { return apiKey; }
    public String getBusinessName() { return businessName; }
    public String getWebhookUrl() { return webhookUrl; }
    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }
}
