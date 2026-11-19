package com.minipayment.resilience;
import org.springframework.stereotype.Component;
@Component
public class HalfOpenCanaryTrafficDistributor { public boolean shouldSample() { return true; } }