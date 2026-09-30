"""
Field and citizen report database model for ground-truth verification.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class FieldReport(Base):
    __tablename__ = "field_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Types: Crack, Slope_Movement, Rockfall, Landslide, Road_Blockage, Flooding, Drainage_Failure, Other
    report_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    severity = Column(String(30), default="medium")  # low, medium, high, critical
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Verification status: 'PENDING', 'VERIFIED', 'REJECTED'
    verification_status = Column(String(30), default="PENDING", index=True)
    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reporter = relationship("User", back_populates="field_reports", foreign_keys=[user_id])
    verifier = relationship("User", back_populates="verified_reports", foreign_keys=[verified_by])
    location = relationship("Location", back_populates="field_reports")
