package com.minipayment.security;
import jakarta.servlet.*;
import java.io.IOException;
import org.springframework.stereotype.Component;
@Component
public class ApiKeyAuthenticationFilter implements Filter { public void doFilter(ServletRequest r, ServletResponse s, FilterChain c) throws IOException, ServletException { c.doFilter(r, s); } }