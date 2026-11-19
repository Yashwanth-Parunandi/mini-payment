package com.minipayment.resilience;
import org.springframework.stereotype.Component;
@Component
public class DynamicThresholdAdjuster { public double getActiveThreshold() { return 20.0; } }