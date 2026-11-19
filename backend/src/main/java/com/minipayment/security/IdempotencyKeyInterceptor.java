package com.minipayment.security;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;
@Component
public class IdempotencyKeyInterceptor implements HandlerInterceptor {}