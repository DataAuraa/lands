"""
Incident and Field Report Simulator for Northeast India Geohazards.
"""
from datetime import datetime
import random
from typing import Dict, Any, List

NER_INCIDENT_TEMPLATES = [
    {
        "report_type": "Crack",
        "description": "Longitudinal tension crack observed along the crown of the road-cut embankment. Approximate length 18m, opening width 8-12cm.",
        "severity": "high",
    },
    {
        "report_type": "Slope_Movement",
        "description": "Creep movement detected on terraced hillside above village settlement. Tilting of electric utility poles and fencing noted.",
        "severity": "critical",
    },
    {
        "report_type": "Rockfall",
        "description": "Fragmented sandstone boulder debris fallen onto the carriage-way of the bypass highway. Single lane blocked.",
        "severity": "medium",
    },
    {
        "report_type": "Road_Blockage",
        "description": "Total mudslide blockage across 45-meter stretch of National Highway. Stranded commercial vehicles present.",
        "severity": "critical",
    },
    {
        "report_type": "Drainage_Failure",
        "description": "Culvert blocked by silt and woody debris causing hill water overflow to erode the slope toe.",
        "severity": "medium",
    },
]


class IncidentGenerator:
    """Generates realistic field reports with realistic geotechnical jargon."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def generate_demo_report(self, location_id: int, lat: float, lon: float, user_id: int = 1) -> Dict[str, Any]:
        template = self.rng.choice(NER_INCIDENT_TEMPLATES)
        # Small GPS jitter around location
        offset_lat = self.rng.uniform(-0.008, 0.008)
        offset_lon = self.rng.uniform(-0.008, 0.008)

        return {
            "user_id": user_id,
            "location_id": location_id,
            "latitude": round(lat + offset_lat, 5),
            "longitude": round(lon + offset_lon, 5),
            "report_type": template["report_type"],
            "description": template["description"],
            "severity": template["severity"],
            "timestamp": datetime.utcnow(),
            "verification_status": "PENDING",
            "image_url": "/media/reports/sample_landslide_crack.jpg",
        }


incident_generator = IncidentGenerator()
