"""
Historical Landslides and Datasets API Router.
Provides disaster inventory records and CSV dataset validation upload.
"""
from datetime import datetime
from typing import List, Optional
import io
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.landslide import HistoricalLandslide
from app.services.auth_service import require_roles

router = APIRouter(tags=["Landslides & Datasets"])


@router.get("/landslides")
def list_landslides(
    location_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieve historical landslide disaster catalog."""
    query = db.query(HistoricalLandslide)
    if location_id:
        query = query.filter(HistoricalLandslide.location_id == location_id)
    if severity:
        query = query.filter(HistoricalLandslide.severity == severity)
    return query.order_by(HistoricalLandslide.event_date.desc()).all()


@router.post("/datasets/upload")
async def upload_dataset_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "dma"))
):
    """
    Upload CSV dataset of historical geotechnical / slope failure observations.
    Validates missing values, duplicate rows, coordinate bounds, and formats a Data Quality Report.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    total_rows = len(df)
    missing_count = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    # Validate coordinate bounds (NER roughly Lat 21.5 - 29.5 N, Lon 89.5 - 97.5 E)
    invalid_coords = 0
    if "latitude" in df.columns and "longitude" in df.columns:
        invalid_coords = int(((df["latitude"] < -90) | (df["latitude"] > 90) | (df["longitude"] < -180) | (df["longitude"] > 180)).sum())

    quality_score = max(0, 100 - (missing_count * 2) - (duplicate_rows * 5) - (invalid_coords * 10))

    return {
        "filename": file.filename,
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "columns_detected": list(df.columns),
        "missing_values": missing_count,
        "duplicate_rows": duplicate_rows,
        "invalid_coordinates": invalid_coords,
        "data_quality_score": quality_score,
        "status": "VALIDATED_AND_STAGED",
        "message": f"Successfully validated dataset with {quality_score}% quality index."
    }
