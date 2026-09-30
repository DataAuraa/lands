"""
Pydantic schemas for ML Predictions, Risk Scoring, and Explanations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    rainfall_24h: float = Field(..., ge=0.0, description="24-hour rainfall accumulation in mm")
    soil_moisture: float = Field(..., ge=0.0, le=100.0, description="Soil moisture percentage")
    slope: float = Field(..., ge=0.0, le=90.0, description="Slope angle in degrees")
    elevation: float = Field(..., description="Elevation in meters")
    historical_susceptibility: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Optional context fields
    rainfall_1h: Optional[float] = 0.0
    rainfall_72h: Optional[float] = 0.0
    change_score: Optional[float] = 0.0
    distance_to_road: Optional[float] = 1.0
    distance_to_river: Optional[float] = 1.0
    land_cover: Optional[str] = "mixed_forest"


class PredictionResponse(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Composite risk score (0-100)")
    risk_level: str = Field(..., description="LOW, MODERATE, HIGH, VERY_HIGH, CRITICAL")
    probability: float = Field(..., ge=0.0, le=1.0)
    model_version: str = "v1.0"
    confidence: float = Field(..., ge=0.0, le=1.0)
    top_factors: List[str]
    explanation: Optional[Dict[str, Any]] = None
    sub_scores: Optional[Dict[str, float]] = None
    timestamp: Optional[datetime] = None
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    disclaimer: str = "This is an AI-generated risk indication and should be interpreted with official disaster-management guidance."


class RiskHeatmapPoint(BaseModel):
    location_id: int
    name: str
    latitude: float
    longitude: float
    risk_score: float
    risk_level: str
    rainfall_24h: float
    soil_moisture: float
    last_updated: datetime
