package com.minipayment.webhook;
import org.springframework.stereotype.Component;
@Component
public class HmacSignatureGenerator { public String sign(String payload, String secret) { return "hmac_sha256_mock"; } }