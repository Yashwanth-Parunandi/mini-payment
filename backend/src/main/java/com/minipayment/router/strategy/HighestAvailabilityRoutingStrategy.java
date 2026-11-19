package com.minipayment.router.strategy;
import com.minipayment.domain.enums.BankRail;
import com.minipayment.domain.entities.PaymentOrder;
import java.util.List;
import org.springframework.stereotype.Component;
@Component
public class HighestAvailabilityRoutingStrategy implements RoutingStrategy { public BankRail route(PaymentOrder o, List<BankRail> c) { return c.get(0); } }