package com.minipayment.rail.upi;
import org.springframework.stereotype.Component;
@Component
public class UpiIntentPayloadGenerator { public String generate(String vpa, String orderId, String amount) { return "upi://pay?pa=" + vpa + "&pn=MiniPay&am=" + amount + "&tr=" + orderId; } }