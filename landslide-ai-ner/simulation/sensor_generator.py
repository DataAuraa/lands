"""
IoT Geotechnical Soil Sensor Simulator.
Simulates ESP32/LoRaWAN field nodes recording volumetric soil moisture, pore pressure, and battery life.
"""
from datetime import datetime
import random
from typing import Dict, Any


class SensorGenerator:
    """Generates geotechnical telemetry reflecting terrain saturation dynamics."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.DATA_SOURCE = "DEMO_SIMULATOR"

    def generate_reading(
        self,
        sensor_id: str,
        location_id: int,
        rainfall_context: float = 0.0,
        forced_saturation: float = None
    ) -> Dict[str, Any]:
        """Generate sensor packet with lagged hydrologic saturation response."""
        if forced_saturation is not None:
            moisture = forced_saturation
        else:
            base = 40.0
            response = min(55.0, (rainfall_context / 150.0) * 55.0)
            noise = self.rng.uniform(-1.5, 1.5)
            moisture = round(min(98.0, max(12.0, base + response + noise)), 1)

        status = "ONLINE"
        battery = round(self.rng.uniform(70.0, 99.0), 1)
        if self.rng.random() < 0.04:
            status = "LOW_BATTERY"
            battery = round(self.rng.uniform(8.0, 18.0), 1)

        return {
            "sensor_id": sensor_id,
            "location_id": location_id,
            "timestamp": datetime.utcnow(),
            "soil_moisture": moisture,
            "soil_temperature": round(self.rng.uniform(18.0, 23.0), 1),
            "soil_pressure": round(101.3 + (moisture / 12.0), 1),
            "battery_level": battery,
            "sensor_status": status,
            "source": self.DATA_SOURCE,
        }
