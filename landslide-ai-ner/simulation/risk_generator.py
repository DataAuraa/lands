"""
Live Event Demonstration Simulator.
Orchestrates the 12-step disaster evolution scenario for Noney District, Manipur (or target demo site).
"""
from typing import Dict, Any, List


class RiskScenarioSimulator:
    """State machine driving the interactive live disaster early warning demo."""

    STEPS: List[Dict[str, Any]] = [
        {
            "step": 1,
            "title": "Normal Baseline Weather",
            "description": "Dry seasonal conditions in Noney Valley. Low precipitation and stable geotechnical readings.",
            "rainfall_1h": 2.0,
            "rainfall_24h": 12.0,
            "soil_moisture": 38.0,
            "risk_score": 14.5,
            "risk_level": "LOW",
            "action": "Baseline status recorded across GIS layers."
        },
        {
            "step": 2,
            "title": "Orographic Rainfall Begins",
            "description": "Monsoon cloudband enters hill range. Moderate rainfall begins across catchment slopes.",
            "rainfall_1h": 18.0,
            "rainfall_24h": 45.0,
            "soil_moisture": 48.0,
            "risk_score": 28.0,
            "risk_level": "MODERATE",
            "action": "Telemetry stream flags rainfall buildup."
        },
        {
            "step": 3,
            "title": "Rainfall Intensifies into Heavy Downpour",
            "description": "Continuous torrential rainfall. Runoff coefficient increases as topsoil reaches initial saturation.",
            "rainfall_1h": 32.0,
            "rainfall_24h": 95.0,
            "soil_moisture": 62.0,
            "risk_score": 38.5,
            "risk_level": "MODERATE",
            "action": "Automated feature vector updated by background worker."
        },
        {
            "step": 4,
            "title": "Soil Moisture Surges & Pore Pressure Rises",
            "description": "IoT piezometer sensors register significant increase in pore-water pressure along steep road-cut slopes.",
            "rainfall_1h": 42.0,
            "rainfall_24h": 140.0,
            "soil_moisture": 76.0,
            "risk_score": 48.0,
            "risk_level": "HIGH",
            "action": "Model inference triggers early alert evaluation."
        },
        {
            "step": 5,
            "title": "AI Risk Score Enters HIGH Tier",
            "description": "Combined trigger score crosses 50. Slope factor of safety begins deteriorating.",
            "rainfall_1h": 48.0,
            "rainfall_24h": 175.0,
            "soil_moisture": 84.0,
            "risk_score": 58.0,
            "risk_level": "HIGH",
            "action": "District Administration notified of elevated vulnerability."
        },
        {
            "step": 6,
            "title": "Severe Saturation — Risk Reaches VERY HIGH",
            "description": "Antecedent moisture reaches critical threshold. Soil cohesion drops significantly.",
            "rainfall_1h": 55.0,
            "rainfall_24h": 210.0,
            "soil_moisture": 91.0,
            "risk_score": 74.0,
            "risk_level": "VERY_HIGH",
            "action": "Automated VERY HIGH alert generated for NH-37 corridor."
        },
        {
            "step": 7,
            "title": "Disaster Alert Generated & Multi-Channel Dispatch",
            "description": "Early Warning Engine broadcasts automated warning bulletin to State DMA, DEOC, and field teams.",
            "rainfall_1h": 60.0,
            "rainfall_24h": 235.0,
            "soil_moisture": 94.0,
            "risk_score": 82.0,
            "risk_level": "CRITICAL",
            "action": "SMS and Push notifications dispatched with official guidance disclaimers."
        },
        {
            "step": 8,
            "title": "Live GIS Map Heatmap Transitions to Critical Purple",
            "description": "Interactive MapLibre GL layer updates risk buffer zone into Critical red/purple contour.",
            "rainfall_1h": 62.0,
            "rainfall_24h": 250.0,
            "soil_moisture": 95.0,
            "risk_score": 88.5,
            "risk_level": "CRITICAL",
            "action": "Real-time WebSocket pushes updated GeoJSON risk polygon to dashboard."
        },
        {
            "step": 9,
            "title": "Multilingual Citizen Notification Received",
            "description": "Citizens and village headmen receive localized notification in English, Hindi, and Assamese/Manipuri.",
            "rainfall_1h": 58.0,
            "rainfall_24h": 260.0,
            "soil_moisture": 96.0,
            "risk_score": 91.0,
            "risk_level": "CRITICAL",
            "action": "Traffic alerted to halt near high-risk railway construction slope."
        },
        {
            "step": 10,
            "title": "Field Officer Submits Geo-Tagged Report",
            "description": "On-ground patrol officer notices tension cracks (15cm wide) on crown of slope and submits mobile report.",
            "rainfall_1h": 52.0,
            "rainfall_24h": 265.0,
            "soil_moisture": 96.0,
            "risk_score": 93.0,
            "risk_level": "CRITICAL",
            "action": "Geo-tagged photo of tension crack submitted via mobile web view."
        },
        {
            "step": 11,
            "title": "District Authority Verifies Incident & Deploys SDRF",
            "description": "Disaster Management Authority reviews field report, verifies high tension crack hazard, and mobilizes SDRF.",
            "rainfall_1h": 40.0,
            "rainfall_24h": 270.0,
            "soil_moisture": 97.0,
            "risk_score": 95.0,
            "risk_level": "CRITICAL",
            "action": "Report status updated to VERIFIED in audit log."
        },
        {
            "step": 12,
            "title": "Active Geo-Hazard Incident Displayed on Command Center GIS",
            "description": "Incident icon pinned onto GIS map with road closure status. Continuous feedback loop completed.",
            "rainfall_1h": 25.0,
            "rainfall_24h": 275.0,
            "soil_moisture": 94.0,
            "risk_score": 86.0,
            "risk_level": "CRITICAL",
            "action": "Full decision loop closed: Weather → Soil → AI → Alert → Field Report → Action."
        }
    ]

    def __init__(self):
        self.current_step_index = 0

    def get_step(self, step_number: int) -> Dict[str, Any]:
        """Get specific scenario step (1 to 12)."""
        idx = max(0, min(len(self.STEPS) - 1, step_number - 1))
        return self.STEPS[idx]

    def get_all_steps(self) -> List[Dict[str, Any]]:
        return self.STEPS


scenario_simulator = RiskScenarioSimulator()
