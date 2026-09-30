"""
Realistic weather simulation calibrated for Northeast India (NER) orographic monsoon regimes.
Clearly labeled as DEMO / SIMULATION data.
"""
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List


class WeatherGenerator:
    """Simulates realistic temporal rainfall and barometric changes in steep hill terrains."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.DATA_SOURCE = "DEMO_SIMULATOR"

    def generate_current(self, location_id: int, lat: float, lon: float) -> Dict[str, Any]:
        """Generate current weather packet."""
        rf_1h = round(self.rng.uniform(0.0, 18.0), 1)
        rf_24h = round(rf_1h * 5.0 + self.rng.uniform(15.0, 95.0), 1)
        rf_72h = round(rf_24h * 1.8, 1)

        return {
            "location_id": location_id,
            "station_id": f"AWS_NER_{location_id:03d}",
            "latitude": lat,
            "longitude": lon,
            "timestamp": datetime.utcnow(),
            "rainfall_1h": rf_1h,
            "rainfall_3h": round(rf_1h * 2.6, 1),
            "rainfall_6h": round(rf_1h * 4.4, 1),
            "rainfall_12h": round(rf_24h * 0.55, 1),
            "rainfall_24h": rf_24h,
            "rainfall_72h": rf_72h,
            "temperature": round(self.rng.uniform(17.0, 24.0), 1),
            "humidity": round(self.rng.uniform(72.0, 98.0), 1),
            "wind_speed": round(self.rng.uniform(4.0, 25.0), 1),
            "pressure": round(self.rng.uniform(998.0, 1010.0), 1),
            "source": self.DATA_SOURCE,
            "is_simulation": True,
        }

    def generate_scenario_progression(self, base_rf: float, intensity_multiplier: float) -> Dict[str, float]:
        """Progress rainfall intensity during demo simulation."""
        rf_1h = round(base_rf * intensity_multiplier, 1)
        rf_24h = round(rf_1h * 8.0, 1)
        rf_72h = round(rf_24h * 1.6, 1)
        return {"rainfall_1h": rf_1h, "rainfall_24h": rf_24h, "rainfall_72h": rf_72h}
