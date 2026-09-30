"""
Pydantic schemas for Location and geospatial GIS objects.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    name: str = Field(..., max_length=150)
    state: str = Field(..., max_length=100)
    district: str = Field(..., max_length=100)
    block: Optional[str] = None
    village: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    elevation: float = Field(default=0.0, description="Elevation in meters")
    population: int = Field(default=0, ge=0)
    road_connectivity: str = "paved"
    infrastructure_type: str = "residential"
    
    slope: float = Field(default=0.0, ge=0.0, le=90.0)
    aspect: float = Field(default=0.0, ge=0.0, le=360.0)
    curvature: float = 0.0
    drainage_density: float = 0.0
    land_cover: str = "mixed_forest"
    geology: str = "sedimentary"
    distance_to_road: float = 1.0
    distance_to_river: float = 1.0


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    population: Optional[int] = None
    road_connectivity: Optional[str] = None
    infrastructure_type: Optional[str] = None
    slope: Optional[float] = None
    elevation: Optional[float] = None
    is_active: Optional[bool] = None


class LocationResponse(LocationBase):
    id: int
    is_active: bool
    created_at: datetime
    latest_risk_score: Optional[float] = None
    latest_risk_level: Optional[str] = None

    class Config:
        from_attributes = True


class GeoJSONGeometry(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
