"""
Pydantic schemas for Soil Sensors and IoT telemetry data.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class SoilSensorCreate(BaseModel):
    sensor_id: str
    location_id: int
    name: str
    latitude: float
    longitude: float


class SoilSensorResponse(BaseModel):
    id: int
    sensor_id: str
    location_id: int
    name: str
    latitude: float
    longitude: float
    is_active: bool
    installed_at: datetime
    latest_soil_moisture: Optional[float] = None
    latest_status: Optional[str] = None
    latest_battery: Optional[float] = None
    last_seen: Optional[datetime] = None

    class Config:
        from_attributes = True


class SensorDataCreate(BaseModel):
    sensor_id: str
    location_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    soil_moisture: float = Field(..., ge=0.0, le=100.0, description="Volumetric water content %")
    soil_temperature: float = 20.0
    soil_pressure: float = 101.3
    battery_level: float = Field(default=100.0, ge=0.0, le=100.0)
    sensor_status: str = Field(default="ONLINE", description="ONLINE, OFFLINE, LOW_BATTERY, ERROR")


class SensorDataResponse(SensorDataCreate):
    id: int
    location_id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True
