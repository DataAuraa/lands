"""
Pydantic schemas for Weather data and forecasts.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class WeatherDataBase(BaseModel):
    station_id: str
    latitude: float
    longitude: float
    rainfall_1h: float = 0.0
    rainfall_3h: float = 0.0
    rainfall_6h: float = 0.0
    rainfall_12h: float = 0.0
    rainfall_24h: float = 0.0
    rainfall_72h: float = 0.0
    temperature: float = 20.0
    humidity: float = 70.0
    wind_speed: float = 5.0
    pressure: float = 1013.25
    source: str = "DEMO"


class WeatherDataCreate(WeatherDataBase):
    timestamp: Optional[datetime] = None


class WeatherDataResponse(WeatherDataBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class WeatherForecastItem(BaseModel):
    timestamp: datetime
    expected_rainfall: float
    temperature: float
    humidity: float
    risk_indicator: str


class WeatherForecastResponse(BaseModel):
    location_id: int
    station_id: str
    source: str
    is_simulation: bool
    generated_at: datetime
    forecast: List[WeatherForecastItem]
