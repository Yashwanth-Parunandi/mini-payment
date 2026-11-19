package com.minipayment.rail.mapper;
import org.springframework.stereotype.Component;
@Component
public class BankResponseCodeMapper { public String mapToStandard(String rawCode) { return "SUCCESS"; } }