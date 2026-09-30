"""
Field Reports and Citizen Observations API Router.
Handles ground-truth crowdsourced incident reporting, media uploads, and DMA verification.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.field_report import FieldReport
from app.models.location import Location
from app.models.user import User
from app.schemas.report import FieldReportCreate, FieldReportUpdate, FieldReportResponse
from app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/reports", tags=["Field Reports"])


@router.get("", response_model=List[FieldReportResponse])
def list_reports(
    verification_status: Optional[str] = Query(None),
    report_type: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieve all submitted ground-truth geohazard observations."""
    query = db.query(FieldReport)
    if verification_status:
        query = query.filter(FieldReport.verification_status == verification_status)
    if report_type:
        query = query.filter(FieldReport.report_type == report_type)
    if location_id:
        query = query.filter(FieldReport.location_id == location_id)

    reports = query.order_by(FieldReport.timestamp.desc()).all()
    results = []
    for r in reports:
        loc = db.query(Location).filter(Location.id == r.location_id).first() if r.location_id else None
        user = db.query(User).filter(User.id == r.user_id).first()
        res = FieldReportResponse.model_validate(r)
        res.location_name = loc.name if loc else "Regional Slope"
        res.reporter_name = user.name if user else "Citizen / Officer"
        results.append(res)
    return results


@router.post("", response_model=FieldReportResponse, status_code=status.HTTP_201_CREATED)
def submit_report(
    report_in: FieldReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Citizen or Officer: Submit a geo-tagged incident or slope tension crack report."""
    report = FieldReport(
        user_id=current_user.id,
        location_id=report_in.location_id,
        latitude=report_in.latitude,
        longitude=report_in.longitude,
        report_type=report_in.report_type,
        description=report_in.description,
        image_url=report_in.image_url,
        video_url=report_in.video_url,
        severity=report_in.severity,
        timestamp=report_in.timestamp or datetime.utcnow(),
        verification_status="PENDING",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    loc = db.query(Location).filter(Location.id == report.location_id).first() if report.location_id else None
    res = FieldReportResponse.model_validate(report)
    res.location_name = loc.name if loc else "Regional Slope"
    res.reporter_name = current_user.name
    return res


@router.patch("/{report_id}", response_model=FieldReportResponse)
def update_report_status(
    report_id: int,
    update_in: FieldReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "dma", "field_officer"))
):
    """Field Officer / DMA: Verify or Reject an on-ground citizen report."""
    report = db.query(FieldReport).filter(FieldReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.verification_status = update_in.verification_status
    report.verified_by = current_user.id
    report.verified_at = datetime.utcnow()
    db.commit()
    db.refresh(report)

    loc = db.query(Location).filter(Location.id == report.location_id).first() if report.location_id else None
    res = FieldReportResponse.model_validate(report)
    res.location_name = loc.name if loc else "Regional Slope"
    res.reporter_name = current_user.name
    return res
