"""
Explainable AI (XAI) utility for Landslide Risk Predictions.
Translates feature importance, tree paths, and geotechnical rules into human-readable narratives.
"""
from typing import Dict, Any, List

FEATURE_DESCRIPTIONS = {
    "rainfall_24h": "Accumulated 24-hour rainfall",
    "rainfall_72h": "Antecedent 72-hour rainfall saturation",
    "rainfall_1h": "Short-duration intense rainfall rate",
    "soil_moisture": "Volumetric soil moisture content / pore water saturation",
    "slope": "Terrain slope angle steepness",
    "elevation": "Topographic elevation",
    "historical_susceptibility": "Baseline geological susceptibility index",
    "change_score": "Satellite surface deformation / vegetation loss indicator",
    "distance_to_road": "Proximity to road-cut excavation slopes",
    "distance_to_river": "Proximity to toe-erosion river channels",
    "drainage_density": "Drainage network density",
}


def explain_prediction(features: Dict[str, Any], risk_score: float) -> List[str]:
    """Generate prioritized top contributing factors for the user interface."""
    factors = []

    rf_24 = features.get("rainfall_24h", 0.0)
    rf_1h = features.get("rainfall_1h", 0.0)
    sm = features.get("soil_moisture", 0.0)
    slope = features.get("slope", 0.0)
    susc = features.get("historical_susceptibility", 0.5)
    change = features.get("change_score", 0.0)

    if rf_24 >= 100.0:
        factors.append(f"Excessive 24-hour rainfall ({rf_24:.1f} mm exceeding critical threshold)")
    elif rf_24 >= 50.0:
        factors.append(f"Elevated 24-hour rainfall ({rf_24:.1f} mm)")

    if rf_1h >= 25.0:
        factors.append(f"Cloudburst-level rainfall intensity ({rf_1h:.1f} mm/hr)")

    if sm >= 80.0:
        factors.append(f"Soil near complete water saturation ({sm:.1f}%), elevating pore-water pressure")
    elif sm >= 65.0:
        factors.append(f"High soil moisture saturation ({sm:.1f}%)")

    if slope >= 35.0:
        factors.append(f"Critical steep slope angle ({slope:.1f}°), exceeding angle of internal friction")
    elif slope >= 25.0:
        factors.append(f"Moderately steep terrain slope ({slope:.1f}°)")

    if susc >= 0.70:
        factors.append(f"High historical geo-susceptibility zone ({susc:.2f})")

    if change >= 0.35:
        factors.append("Recent land-cover alteration or scar deformation detected by satellite")

    if not factors:
        factors.append("Normal terrain and baseline moisture parameters within seasonal safe limits")

    return factors[:5]


def get_risk_narrative(risk_level: str, top_factors: List[str], location_name: str) -> str:
    """Generate a coherent decision-support briefing narrative."""
    bullets = "\n".join([f" • {f}" for f in top_factors])
    return (
        f"Early Warning Assessment for {location_name}:\n"
        f"Assigned Risk Tier: {risk_level}.\n\n"
        f"Primary Geotechnical & Meteorological Drivers:\n"
        f"{bullets}\n\n"
        f"Advisory: This assessment is an automated decision-support indication intended for disaster "
        f"authorities and field verification teams. Refer to official state emergency directives."
    )
