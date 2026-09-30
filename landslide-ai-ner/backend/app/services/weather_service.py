"""
Weather Ingestion Adapter.
Abstracts official IMD (India Meteorological Department) API and
provides calibrated NER synthetic simulation data when API keys are absent.
"""
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List
import httpx

from app.config import settings


class WeatherAdapter:
    """Standardized Weather Adapter interface."""

    def __init__(self):
        self.api_key = settings.IMD_API_KEY
        self.base_url = settings.IMD_API_BASE_URL
        self.is_demo = settings.SIMULATION_MODE or not bool(self.api_key)

    async def get_current_data(self, station_id: str, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch current weather for location coordinates."""
        if not self.is_demo and self.api_key:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(
                        f"{self.base_url}/current",
                        params={"lat": lat, "lon": lon, "api_key": self.api_key}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        data["source"] = "IMD"
                        return data
            except Exception:
                # Graceful fallback to offline/last known/demo with clear labeling
                pass

        # Realistic simulation for Northeast India Monsoon
        random.seed(int(lat * 100) + int(lon * 100) + datetime.utcnow().hour)
        rf_1h = round(random.uniform(0.0, 15.0), 1)
        rf_24h = round(rf_1h * random.uniform(4.0, 10.0) + random.uniform(10.0, 80.0), 1)
        rf_72h = round(rf_24h * random.uniform(1.5, 2.5), 1)

        return {
            "station_id": station_id,
            "latitude": lat,
            "longitude": lon,
            "timestamp": datetime.utcnow(),
            "rainfall_1h": rf_1h,
            "rainfall_3h": round(rf_1h * 2.5, 1),
            "rainfall_6h": round(rf_1h * 4.2, 1),
            "rainfall_12h": round(rf_24h * 0.6, 1),
            "rainfall_24h": rf_24h,
            "rainfall_72h": rf_72h,
            "temperature": round(random.uniform(16.0, 26.0), 1),
            "humidity": round(random.uniform(70.0, 96.0), 1),
            "wind_speed": round(random.uniform(3.0, 28.0), 1),
            "pressure": round(random.uniform(995.0, 1012.0), 1),
            "source": "DEMO (SIMULATED)",
            "is_simulation": True,
        }

    async def get_forecast(self, location_id: int, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Return 72-hour forecast items in 6-hour intervals."""
        forecast = []
        now = datetime.utcnow()
        for i in range(1, 13):
            step_time = now + timedelta(hours=i * 6)
            expected_rf = round(random.uniform(5.0, 45.0), 1)
            risk_label = "HIGH" if expected_rf > 30 else ("MODERATE" if expected_rf > 15 else "LOW")
            forecast.append({
                "timestamp": step_time,
                "expected_rainfall": expected_rf,
                "temperature": round(random.uniform(17.0, 25.0), 1),
                "humidity": round(random.uniform(75.0, 95.0), 1),
                "risk_indicator": risk_label,
            })
        return forecast

    async def get_historical(self, location_id: int, hours: int = 72) -> List[Dict[str, Any]]:
        """Generate historical hourly rainfall timeline for charts."""
        records = []
        now = datetime.utcnow()
        for h in range(hours, 0, -1):
            t = now - timedelta(hours=h)
            records.append({
                "timestamp": t,
                "rainfall_1h": round(random.uniform(0.0, 12.0), 1),
                "temperature": round(22.0 + 3.0 * random.uniform(-1, 1), 1),
                "humidity": round(80.0 + 10.0 * random.uniform(-1, 1), 1),
            })
        return records


weather_adapter = WeatherAdapter()
