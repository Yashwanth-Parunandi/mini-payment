package com.minipayment.webhook;
import java.time.Instant;
import java.util.UUID;
public record WebhookPayload(UUID eventId, String eventType, Object payload, Instant timestamp) {}