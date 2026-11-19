package com.minipayment.controller;

import com.minipayment.domain.entities.PaymentOrder;
import com.minipayment.dto.InitiatePaymentRequest;
import com.minipayment.dto.PaymentResponse;
import com.minipayment.repository.PaymentOrderRepository;
import com.minipayment.service.PaymentOrchestratorService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/payments")
public class PaymentController {
    private final PaymentOrchestratorService orchestratorService;
    private final PaymentOrderRepository orderRepository;

    public PaymentController(PaymentOrchestratorService orchestratorService, PaymentOrderRepository orderRepository) {
        this.orchestratorService = orchestratorService;
        this.orderRepository = orderRepository;
    }

    @PostMapping
    public ResponseEntity<PaymentResponse> initiatePayment(
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @Valid @RequestBody InitiatePaymentRequest request) {

        String key = (idempotencyKey != null && !idempotencyKey.isBlank()) 
                ? idempotencyKey 
                : UUID.randomUUID().toString();

        Optional<PaymentOrder> existing = orderRepository.findByIdempotencyKey(key);
        if (existing.isPresent()) {
            return ResponseEntity.ok(PaymentResponse.from(existing.get()));
        }

        PaymentOrder order = new PaymentOrder(
                request.getMerchantOrderId(),
                key,
                request.getAmount(),
                request.getCurrency(),
                request.getPaymentMethod()
        );

        PaymentOrder saved = orchestratorService.processPayment(order);
        return ResponseEntity.ok(PaymentResponse.from(saved));
    }

    @GetMapping("/{id}")
    public ResponseEntity<PaymentResponse> getPayment(@PathVariable UUID id) {
        return orderRepository.findById(id)
                .map(order -> ResponseEntity.ok(PaymentResponse.from(order)))
                .orElse(ResponseEntity.notFound().build());
    }
}
