package com.minipayment.domain.entities;
import jakarta.persistence.*;
import java.util.UUID;
@Entity @Table(name="device_fingerprints")
public class DeviceFingerprint extends AuditableEntity { @Id @GeneratedValue private UUID id; }