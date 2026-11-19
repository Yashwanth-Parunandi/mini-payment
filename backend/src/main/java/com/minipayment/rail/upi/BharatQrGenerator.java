package com.minipayment.rail.upi;
import org.springframework.stereotype.Component;
@Component
public class BharatQrGenerator { public String generateQr(String upiUri) { return "data:image/svg+xml;mockQr"; } }