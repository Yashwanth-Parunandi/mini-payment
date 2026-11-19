package com.minipayment.resilience;

import com.minipayment.domain.enums.BankRail;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.data.redis.core.ListOperations;
import org.springframework.data.redis.core.RedisTemplate;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class RedisSlidingWindowTrackerTest {
    private RedisTemplate<String, Object> redisTemplate;
    private RedisSlidingWindowTracker tracker;

    @BeforeEach
    void setUp() {
        redisTemplate = Mockito.mock(RedisTemplate.class);
        ListOperations listOps = Mockito.mock(ListOperations.class);
        when(redisTemplate.opsForList()).thenReturn(listOps);
        tracker = new RedisSlidingWindowTracker(redisTemplate);
    }

    @Test
    void testSuccessRateCalculation() {
        for (int i = 0; i < 8; i++) {
            tracker.recordCall(BankRail.HDFC_RAIL, true, 100);
        }
        for (int i = 0; i < 2; i++) {
            tracker.recordCall(BankRail.HDFC_RAIL, false, 250);
        }
        assertEquals(80.0, tracker.getSuccessRate(BankRail.HDFC_RAIL), 0.01);
    }

    @Test
    void testP90LatencyCalculation() {
        for (int i = 1; i <= 10; i++) {
            tracker.recordCall(BankRail.AXIS_UPI_RAIL, true, i * 10);
        }
        long p90 = tracker.getP90LatencyMs(BankRail.AXIS_UPI_RAIL);
        assertEquals(90, p90);
    }
}
