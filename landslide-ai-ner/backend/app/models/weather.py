"""
Weather data database model.
Tracks multi-window rainfall accumulation, temperature, humidity, wind, and atmospheric pressure.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Rainfall accumulation across critical disaster warning windows (mm)
    rainfall_1h = Column(Float, default=0.0)
    rainfall_3h = Column(Float, default=0.0)
    rainfall_6h = Column(Float, default=0.0)
    rainfall_12h = Column(Float, default=0.0)
    rainfall_24h = Column(Float, default=0.0)
    rainfall_72h = Column(Float, default=0.0)
    
    # Meteorological parameters
    temperature = Column(Float, default=20.0)  # Celsius
    humidity = Column(Float, default=70.0)     # %
    wind_speed = Column(Float, default=5.0)    # km/h
    pressure = Column(Float, default=1013.25)  # hPa
    
    # Provenance: 'IMD' for official or 'DEMO' for simulation
    source = Column(String(30), default="DEMO", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
