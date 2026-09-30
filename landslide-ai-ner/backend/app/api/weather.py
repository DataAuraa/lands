"""
Weather API Router.
Provides current precipitation, hourly histories, and forecasts.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.location import Location
from app.models.weather import WeatherData
from app.schemas.weather import WeatherDataResponse, WeatherForecastResponse
from app.services.weather_service import weather_adapter

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current")
async def get_current_weather(
    location_id: int = Query(..., description="Target Location ID"),
    db: Session = Depends(get_db)
):
    """Retrieve real-time precipitation and atmospheric conditions."""
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    weather_data = await weather_adapter.get_current_data(
        station_id=f"AWS_{loc.id}",
        lat=loc.latitude,
        lon=loc.longitude
    )
    return weather_data


@router.get("/forecast", response_model=WeatherForecastResponse)
async def get_forecast(
    location_id: int = Query(..., description="Target Location ID"),
    db: Session = Depends(get_db)
):
    """Retrieve multi-day probabilistic precipitation forecast."""
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    forecast_items = await weather_adapter.get_forecast(location_id, loc.latitude, loc.longitude)
    return {
        "location_id": location_id,
        "station_id": f"AWS_{loc.id}",
        "source": "DEMO (SIMULATED)" if weather_adapter.is_demo else "IMD",
        "is_simulation": weather_adapter.is_demo,
        "generated_at": forecast_items[0]["timestamp"] if forecast_items else None,
        "forecast": forecast_items
    }


@router.get("/history")
async def get_rainfall_history(
    location_id: int = Query(..., description="Target Location ID"),
    hours: int = Query(72, ge=6, le=168),
    db: Session = Depends(get_db)
):
    """Retrieve time-series hourly rainfall data for charts."""
    records = await weather_adapter.get_historical(location_id, hours=hours)
    return records
