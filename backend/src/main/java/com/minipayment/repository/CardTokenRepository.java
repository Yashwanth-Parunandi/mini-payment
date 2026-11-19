package com.minipayment.repository;
import com.minipayment.domain.entities.CardToken;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;
public interface CardTokenRepository extends JpaRepository<CardToken, UUID> {}