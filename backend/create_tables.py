# =========================================================
# ThreatX — Create Database Tables
# =========================================================

from backend.database import Base, engine
from backend.models import TrafficLog


print("Creating ThreatX database tables...")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")