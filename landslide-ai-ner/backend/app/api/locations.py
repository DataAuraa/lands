"""
Locations API Router.
Manages monitored landslide geozones, terrain parameters, and location queries.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.location import Location
from app.models.prediction import Prediction
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse
from app.services.auth_service import require_roles, get_current_user

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("", response_model=List[LocationResponse])
def list_locations(
    state: Optional[str] = Query(None, description="Filter by NER State"),
    district: Optional[str] = Query(None, description="Filter by District"),
    db: Session = Depends(get_db)
):
    """Retrieve all monitored slope zones across Northeast India."""
    query = db.query(Location).filter(Location.is_active == True)
    if state:
        query = query.filter(Location.state.ilike(f"%{state}%"))
    if district:
        query = query.filter(Location.district.ilike(f"%{district}%"))

    locations = query.all()

    # Populate latest prediction risk level and score for each
    results = []
    for loc in locations:
        latest_pred = (
            db.query(Prediction)
            .filter(Prediction.location_id == loc.id)
            .order_by(Prediction.timestamp.desc())
            .first()
        )
        res = LocationResponse.model_validate(loc)
        if latest_pred:
            res.latest_risk_score = latest_pred.risk_score
            res.latest_risk_level = latest_pred.risk_level
        results.append(res)

    return results


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    """Retrieve single location details with latest condition indicators."""
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    latest_pred = (
        db.query(Prediction)
        .filter(Prediction.location_id == loc.id)
        .order_by(Prediction.timestamp.desc())
        .first()
    )
    res = LocationResponse.model_validate(loc)
    if latest_pred:
        res.latest_risk_score = latest_pred.risk_score
        res.latest_risk_level = latest_pred.risk_level
    return res


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    loc_in: LocationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "dma"))
):
    """Admin / DMA: Add new monitored landslide geozone."""
    loc = Location(**loc_in.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    loc_update: LocationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "dma"))
):
    """Update location parameters or status."""
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    for k, v in loc_update.model_dump(exclude_unset=True).items():
        setattr(loc, k, v)

    db.commit()
    db.refresh(loc)
    return loc
