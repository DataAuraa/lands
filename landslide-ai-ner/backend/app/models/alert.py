"""
Disaster alerts database model.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(String(50), default="AUTOMATED_RISK_TRIGGER")
    # Risk Level: 'LOW', 'MODERATE', 'HIGH', 'VERY_HIGH', 'CRITICAL'
    risk_level = Column(String(30), nullable=False, index=True)
    message = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)
    # Delivery status: 'PENDING', 'SENT', 'FAILED'
    delivery_status = Column(String(30), default="SENT")
    recipient_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

    # Relationships
    location = relationship("Location", back_populates="alerts")
