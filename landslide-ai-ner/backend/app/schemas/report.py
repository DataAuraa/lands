"""
Pydantic schemas for Field and Citizen Reports.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FieldReportCreate(BaseModel):
    location_id: Optional[int] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    # Types: Crack, Slope Movement, Rockfall, Landslide, Road Blockage, Flooding, Drainage Failure, Other
    report_type: str = Field(..., description="Observed geohazard type")
    description: str = Field(..., min_length=5)
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical
    timestamp: Optional[datetime] = None


class FieldReportUpdate(BaseModel):
    verification_status: str = Field(..., description="VERIFIED, REJECTED, PENDING")
    notes: Optional[str] = None


class FieldReportResponse(BaseModel):
    id: int
    user_id: int
    reporter_name: Optional[str] = None
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    latitude: float
    longitude: float
    report_type: str
    description: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    severity: str
    timestamp: datetime
    verification_status: str
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
