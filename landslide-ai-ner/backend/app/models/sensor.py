"""
IoT Soil Sensor database models.
Supports simulated IoT stream and real hardware gateways (ESP32/LoRaWAN).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SoilSensor(Base):
    __tablename__ = "soil_sensors"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(50), unique=True, index=True, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    installed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="sensors")
    readings = relationship("SoilSensorData", back_populates="sensor", cascade="all, delete-orphan", order_by="desc(SoilSensorData.timestamp)")


class SoilSensorData(Base):
    __tablename__ = "soil_sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(50), ForeignKey("soil_sensors.sensor_id"), index=True, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    soil_moisture = Column(Float, nullable=False)     # % volumetric water content (0-100)
    soil_temperature = Column(Float, default=20.0)    # Celsius
    soil_pressure = Column(Float, default=101.3)      # kPa / pore water pressure
    battery_level = Column(Float, default=100.0)      # % (0-100)
    # Status: ONLINE, OFFLINE, LOW_BATTERY, ERROR
    sensor_status = Column(String(30), default="ONLINE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sensor = relationship("SoilSensor", back_populates="readings")
