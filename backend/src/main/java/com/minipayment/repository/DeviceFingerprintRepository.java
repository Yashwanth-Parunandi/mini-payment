package com.minipayment.repository;
import com.minipayment.domain.entities.DeviceFingerprint;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;
public interface DeviceFingerprintRepository extends JpaRepository<DeviceFingerprint, UUID> {}