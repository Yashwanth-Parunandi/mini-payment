package com.minipayment.repository;
import com.minipayment.domain.entities.WebhookSubscription;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;
public interface WebhookSubscriptionRepository extends JpaRepository<WebhookSubscription, UUID> {}