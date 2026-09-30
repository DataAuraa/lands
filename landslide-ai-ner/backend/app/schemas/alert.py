"""
Pydantic schemas for Disaster Alerts and Notifications.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    location_id: int
    alert_type: str = "MANUAL_DISASTER_ALERT"
    risk_level: str = Field(..., description="LOW, MODERATE, HIGH, VERY_HIGH, CRITICAL")
    message: str
    language: str = "en"
    expires_at: Optional[datetime] = None


class AlertAcknowledge(BaseModel):
    acknowledged_by: Optional[int] = None
    notes: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    location_id: int
    location_name: Optional[str] = None
    alert_type: str
    risk_level: str
    message: str
    language: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    delivery_status: str
    recipient_count: int
    is_active: bool
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None

    class Config:
        from_attributes = True
