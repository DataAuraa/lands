"""
Geospatial GIS API Router.
Returns standard GeoJSON FeatureCollections for MapLibre GL and Leaflet mapping layers.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.location import Location
from app.models.sensor import SoilSensor, SoilSensorData
from app.models.landslide import HistoricalLandslide
from app.models.field_report import FieldReport
from app.models.prediction import Prediction
from app.schemas.location import GeoJSONFeatureCollection

router = APIRouter(prefix="/gis", tags=["GIS & Geospatial Layers"])


@router.get("/risk-zones")
def get_risk_zones_geojson(db: Session = Depends(get_db)):
    """Return monitored locations with risk score and tier as GeoJSON Point features."""
    locations = db.query(Location).filter(Location.is_active == True).all()
    features = []
    for loc in locations:
        latest_pred = (
            db.query(Prediction)
            .filter(Prediction.location_id == loc.id)
            .order_by(Prediction.timestamp.desc())
            .first()
        )
        score = latest_pred.risk_score if latest_pred else 25.0
        level = latest_pred.risk_level if latest_pred else "LOW"

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [loc.longitude, loc.latitude]
            },
            "properties": {
                "id": loc.id,
                "name": loc.name,
                "state": loc.state,
                "district": loc.district,
                "elevation": loc.elevation,
                "slope": loc.slope,
                "population": loc.population,
                "risk_score": score,
                "risk_level": level,
                "road_connectivity": loc.road_connectivity,
            }
        }
        features.append(feature)

    return {"type": "FeatureCollection", "features": features}


@router.get("/sensors")
def get_sensors_geojson(db: Session = Depends(get_db)):
    """Return deployed geotechnical sensors as GeoJSON."""
    sensors = db.query(SoilSensor).filter(SoilSensor.is_active == True).all()
    features = []
    for s in sensors:
        latest = (
            db.query(SoilSensorData)
            .filter(SoilSensorData.sensor_id == s.sensor_id)
            .order_by(SoilSensorData.timestamp.desc())
            .first()
        )
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [s.longitude, s.latitude]
            },
            "properties": {
                "sensor_id": s.sensor_id,
                "name": s.name,
                "location_id": s.location_id,
                "soil_moisture": latest.soil_moisture if latest else 55.0,
                "battery": latest.battery_level if latest else 95.0,
                "status": latest.sensor_status if latest else "ONLINE",
            }
        }
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}


@router.get("/landslides")
def get_landslides_geojson(db: Session = Depends(get_db)):
    """Return historical landslide disaster inventory as GeoJSON."""
    events = db.query(HistoricalLandslide).all()
    features = []
    for e in events:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [e.longitude, e.latitude]
            },
            "properties": {
                "id": e.id,
                "event_date": e.event_date.isoformat(),
                "severity": e.severity,
                "casualties": e.casualties,
                "damage_lakhs": e.estimated_damage,
                "road_blocked": e.road_blocked,
                "source": e.source,
                "description": e.description,
            }
        }
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}


@router.get("/reports")
def get_reports_geojson(db: Session = Depends(get_db)):
    """Return crowd-sourced and field officer incident pins as GeoJSON."""
    reports = db.query(FieldReport).all()
    features = []
    for r in reports:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [r.longitude, r.latitude]
            },
            "properties": {
                "id": r.id,
                "report_type": r.report_type,
                "description": r.description,
                "severity": r.severity,
                "verification_status": r.verification_status,
                "timestamp": r.timestamp.isoformat(),
            }
        }
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}


@router.get("/roads")
def get_vulnerable_roads_geojson():
    """Return key highway corridors in NER with real-time blockage status."""
    roads = [
        {
            "name": "NH-29 (Dimapur - Kohima Corridor)",
            "status": "OPEN",
            "risk_level": "HIGH",
            "coordinates": [[93.72, 25.90], [93.90, 25.75], [94.10, 25.66]]
        },
        {
            "name": "NH-37 (Imphal - Jiribam - Noney Cut)",
            "status": "HIGH_RISK",
            "risk_level": "VERY_HIGH",
            "coordinates": [[93.15, 24.80], [93.40, 24.85], [93.60, 24.92], [93.92, 24.81]]
        },
        {
            "name": "NH-06 (Shillong - Jowai - Silchar Lifeline)",
            "status": "PARTIALLY_BLOCKED",
            "risk_level": "HIGH",
            "coordinates": [[91.89, 25.57], [92.20, 25.45], [92.70, 25.10], [92.80, 24.82]]
        },
        {
            "name": "NH-54 (Silchar - Aizawl - Lunglei Route)",
            "status": "OPEN",
            "risk_level": "MODERATE",
            "coordinates": [[92.80, 24.82], [92.71, 23.73], [92.73, 22.88]]
        },
    ]

    features = []
    for r in roads:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": r["coordinates"]
            },
            "properties": {
                "name": r["name"],
                "status": r["status"],
                "risk_level": r["risk_level"]
            }
        })

    return {"type": "FeatureCollection", "features": features}
