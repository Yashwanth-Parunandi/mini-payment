package com.minipayment.repository;

import com.minipayment.domain.entities.RailHealthMetric;
import com.minipayment.domain.enums.BankRail;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Repository
public interface RailHealthMetricRepository extends JpaRepository<RailHealthMetric, UUID> {
    List<RailHealthMetric> findByRailOrderByRecordedAtDesc(BankRail rail);

    @Query("SELECT r FROM RailHealthMetric r WHERE r.rail = :rail AND r.recordedAt >= :since ORDER BY r.recordedAt ASC")
    List<RailHealthMetric> findRecentMetrics(@Param("rail") BankRail rail, @Param("since") Instant since);
}
