package com.minipayment.repository;
import com.minipayment.domain.entities.WebhookDeliveryAttempt;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;
public interface WebhookDeliveryAttemptRepository extends JpaRepository<WebhookDeliveryAttempt, UUID> {}