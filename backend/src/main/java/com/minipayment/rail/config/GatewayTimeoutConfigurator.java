package com.minipayment.rail.config;
import org.springframework.stereotype.Component;
@Component
public class GatewayTimeoutConfigurator { public long getTimeoutMs(String rail) { return 3000L; } }