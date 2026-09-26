# =========================================================
# ThreatX — Database Models
# =========================================================

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from backend.database import Base


# =========================================================
# TRAFFIC LOG
# =========================================================

class TrafficLog(Base):

    __tablename__ = "traffic_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    prediction = Column(
        String(50),
        nullable=False
    )

    attack_category = Column(
        String(100),
        nullable=True
    )

    confidence = Column(
        Float,
        nullable=False
    )

    protocol = Column(
        String(20),
        nullable=True
    )

    service = Column(
        String(50),
        nullable=True
    )

    state = Column(
        String(20),
        nullable=True
    )


# =========================================================
# ALERT
# =========================================================

class Alert(Base):

    __tablename__ = "alerts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    type = Column(
        String(100),
        nullable=False
    )

    severity = Column(
        String(20),
        nullable=False
    )

    description = Column(
        String(500),
        nullable=False
    )

    status = Column(
        String(20),
        default="active",
        nullable=False
    )