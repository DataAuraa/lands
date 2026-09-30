"""
IoT Soil Sensor Adapter.
Manages telemetry ingestion from real ESP32/LoRaWAN gateways or generates
calibrated geotechnical simulations (soil moisture, pore pressure, battery).
"""
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.sensor import SoilSensor, SoilSensorData


class SensorAdapter:
    """Telemetry ingestion and simulation adapter for geotechnical sensors."""

    def ingest_reading(self, db: Session, payload: Dict[str, Any]) -> SoilSensorData:
        """Process incoming IoT sensor packet."""
        reading = SoilSensorData(
            sensor_id=payload["sensor_id"],
            location_id=payload["location_id"],
            timestamp=payload.get("timestamp") or datetime.utcnow(),
            soil_moisture=payload["soil_moisture"],
            soil_temperature=payload.get("soil_temperature", 20.0),
            soil_pressure=payload.get("soil_pressure", 101.3),
            battery_level=payload.get("battery_level", 95.0),
            sensor_status=payload.get("sensor_status", "ONLINE"),
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)
        return reading

    def generate_simulated_reading(self, sensor: SoilSensor, rainfall_intensity: float = 0.0) -> Dict[str, Any]:
        """Generate realistic soil response based on rainfall context."""
        # Soil moisture responds with lag to rainfall
        base_moisture = 45.0
        rain_boost = min(48.0, rainfall_intensity * 0.8)
        noise = random.uniform(-2.0, 2.0)
        moisture = min(98.0, max(15.0, base_moisture + rain_boost + noise))
        
        status = "ONLINE"
        battery = round(random.uniform(75.0, 100.0), 1)
        if random.random() < 0.05:
            status = "LOW_BATTERY"
            battery = round(random.uniform(10.0, 19.0), 1)

        return {
            "sensor_id": sensor.sensor_id,
            "location_id": sensor.location_id,
            "timestamp": datetime.utcnow(),
            "soil_moisture": round(moisture, 1),
            "soil_temperature": round(random.uniform(18.0, 24.0), 1),
            "soil_pressure": round(101.0 + (moisture / 10.0), 1),
            "battery_level": battery,
            "sensor_status": status,
        }


sensor_adapter = SensorAdapter()
