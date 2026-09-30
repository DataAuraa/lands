"""
Satellite and Remote Sensing API Router.
Provides spectral indices (NDVI, NDMI) and surface deformation change scores.
"""
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.location import Location
from app.models.satellite import SatelliteData

router = APIRouter(prefix="/satellite", tags=["Satellite"])


@router.get("")
def get_latest_satellite(location_id: int = Query(...), db: Session = Depends(get_db)):
    """Retrieve latest remote sensing telemetry for monitored hill slope."""
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    sat = (
        db.query(SatelliteData)
        .filter(SatelliteData.location_id == location_id)
        .order_by(SatelliteData.acquisition_time.desc())
        .first()
    )

    if sat:
        return {
            "location_id": sat.location_id,
            "satellite_name": sat.satellite_name,
            "acquisition_time": sat.acquisition_time,
            "ndvi": sat.ndvi,
            "ndmi": sat.ndmi,
            "change_score": sat.change_score,
            "cloud_percentage": sat.cloud_percentage,
            "image_url": sat.image_url or "/media/satellite/sample_sentinel2_rgb.jpg",
            "source": sat.source,
        }

    # Calibrated synthetic satellite indicator
    return {
        "location_id": location_id,
        "satellite_name": "Sentinel-2 (MSI)",
        "acquisition_time": datetime.utcnow() - timedelta(days=2),
        "ndvi": round(random.uniform(0.55, 0.78), 2),
        "ndmi": round(random.uniform(0.35, 0.65), 2),
        "change_score": 0.08,
        "cloud_percentage": 14.5,
        "image_url": "/media/satellite/sample_sentinel2_rgb.jpg",
        "source": "DEMO / SYNTHETIC",
        "is_simulation": True,
    }
