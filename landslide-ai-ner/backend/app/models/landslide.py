"""
Historical landslide catalog database model for Northeast India.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class HistoricalLandslide(Base):
    __tablename__ = "historical_landslides"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    event_date = Column(DateTime, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Severity: 'minor', 'moderate', 'major', 'catastrophic'
    severity = Column(String(50), default="moderate", nullable=False)
    rainfall_before_event = Column(Float, default=0.0)  # mm (antecedent rainfall)
    estimated_damage = Column(Float, default=0.0)       # in Lakhs INR
    road_blocked = Column(Boolean, default=False)
    casualties = Column(Integer, default=0)
    source = Column(String(100), default="GSI / BRO / State DMA")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="historical_events")
