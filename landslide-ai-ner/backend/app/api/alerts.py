"""
Alerts API Router.
Handles active disaster warnings, alert acknowledgements, and manual broadcasts.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.models.location import Location
from app.schemas.alert import AlertCreate, AlertResponse, AlertAcknowledge
from app.services.auth_service import require_roles, get_current_user
from app.models.user import User

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse])
def list_alerts(
    active_only: bool = Query(True, alias="active"),
    risk_level: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """List early warning disaster alerts."""
    query = db.query(Alert)
    if active_only:
        query = query.filter(Alert.is_active == True)
    if risk_level:
        query = query.filter(Alert.risk_level == risk_level)
    if location_id:
        query = query.filter(Alert.location_id == location_id)

    alerts = query.order_by(Alert.created_at.desc()).all()
    results = []
    for a in alerts:
        loc = db.query(Location).filter(Location.id == a.location_id).first()
        res = AlertResponse.model_validate(a)
        res.location_name = loc.name if loc else f"Location #{a.location_id}"
        results.append(res)
    return results


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_manual_alert(
    alert_in: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "district_admin", "dma"))
):
    """Authority: Issue targeted emergency bulletin to field personnel and residents."""
    loc = db.query(Location).filter(Location.id == alert_in.location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    alert = Alert(
        location_id=alert_in.location_id,
        alert_type=alert_in.alert_type,
        risk_level=alert_in.risk_level,
        message=alert_in.message,
        language=alert_in.language,
        created_at=datetime.utcnow(),
        expires_at=alert_in.expires_at,
        delivery_status="SENT",
        recipient_count=loc.population or 100,
        is_active=True
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    res = AlertResponse.model_validate(alert)
    res.location_name = loc.name
    return res


@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    ack: AlertAcknowledge,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Field officer / District Admin: Acknowledge receipt of emergency alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged_by = current_user.id
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)

    loc = db.query(Location).filter(Location.id == alert.location_id).first()
    res = AlertResponse.model_validate(alert)
    res.location_name = loc.name if loc else f"Location #{alert.location_id}"
    return res
