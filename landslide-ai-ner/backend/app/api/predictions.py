"""
Predictions and Risk Engine API Router.
Handles ML inference, on-demand prediction runs, and GIS heatmap synthesis.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.location import Location
from app.models.prediction import Prediction
from app.models.weather import WeatherData
from app.models.sensor import SoilSensorData
from app.schemas.prediction import PredictionInput, PredictionResponse, RiskHeatmapPoint
from ml.predict import predictor
from app.services.alert_service import alert_service

router = APIRouter(tags=["Predictions & Risk"])


@router.post("/ml/predict", response_model=PredictionResponse)
def direct_ml_prediction(input_data: PredictionInput):
    """
    Direct model inference endpoint.
    Accepts raw environmental features and returns risk score, categorical tier, probability, and top factors.
    """
    res = predictor.predict(input_data.model_dump())
    return res


@router.post("/predictions/run", response_model=PredictionResponse)
def run_prediction_for_location(
    location_id: int = Query(..., description="Target Location ID"),
    db: Session = Depends(get_db)
):
    """
    Run early warning prediction on the latest live/demo data for the specified location.
    Saves the prediction to database and evaluates alert thresholds.
    """
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    # Fetch latest soil moisture reading
    latest_sensor = (
        db.query(SoilSensorData)
        .filter(SoilSensorData.location_id == loc.id)
        .order_by(SoilSensorData.timestamp.desc())
        .first()
    )
    soil_moisture = latest_sensor.soil_moisture if latest_sensor else 65.0

    # Fetch latest weather reading
    latest_weather = (
        db.query(WeatherData)
        .filter(WeatherData.latitude == loc.latitude)
        .order_by(WeatherData.timestamp.desc())
        .first()
    )
    rf_24 = latest_weather.rainfall_24h if latest_weather else 85.0
    rf_72 = latest_weather.rainfall_72h if latest_weather else 140.0
    rf_1 = latest_weather.rainfall_1h if latest_weather else 12.0

    features = {
        "rainfall_24h": rf_24,
        "rainfall_72h": rf_72,
        "rainfall_1h": rf_1,
        "soil_moisture": soil_moisture,
        "slope": loc.slope or 30.0,
        "elevation": loc.elevation or 1000.0,
        "historical_susceptibility": 0.70,
        "change_score": 0.1,
    }

    pred_res = predictor.predict(features)

    # Persist prediction in DB
    db_pred = Prediction(
        location_id=loc.id,
        timestamp=datetime.utcnow(),
        risk_score=pred_res["risk_score"],
        risk_level=pred_res["risk_level"],
        probability=pred_res["probability"],
        model_version=pred_res["model_version"],
        confidence=pred_res["confidence"],
        prediction_horizon=24,
        explanation={"top_factors": pred_res["top_factors"]},
        features_used=features
    )
    db.add(db_pred)
    db.commit()

    # Check and trigger alert if applicable
    alert_service.evaluate_and_trigger(db, loc, pred_res)

    pred_res["timestamp"] = db_pred.timestamp
    pred_res["location_id"] = loc.id
    pred_res["location_name"] = loc.name
    return pred_res


@router.get("/predictions", response_model=List[PredictionResponse])
def get_prediction_history(
    location_id: int = Query(...),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve historical prediction records for a location."""
    preds = (
        db.query(Prediction)
        .filter(Prediction.location_id == location_id)
        .order_by(Prediction.timestamp.desc())
        .limit(limit)
        .all()
    )
    results = []
    for p in preds:
        top_f = []
        if p.explanation and isinstance(p.explanation, dict):
            top_f = p.explanation.get("top_factors", [])
        results.append(PredictionResponse(
            risk_score=p.risk_score,
            risk_level=p.risk_level,
            probability=p.probability,
            model_version=p.model_version,
            confidence=p.confidence,
            top_factors=top_f,
            timestamp=p.timestamp,
            location_id=p.location_id,
        ))
    return results


@router.get("/risk/current", response_model=List[RiskHeatmapPoint])
def get_current_risk(db: Session = Depends(get_db)):
    """Retrieve latest risk scores for all monitored locations."""
    locations = db.query(Location).filter(Location.is_active == True).all()
    points = []
    for loc in locations:
        latest = (
            db.query(Prediction)
            .filter(Prediction.location_id == loc.id)
            .order_by(Prediction.timestamp.desc())
            .first()
        )
        score = latest.risk_score if latest else 25.0
        level = latest.risk_level if latest else "LOW"
        points.append(RiskHeatmapPoint(
            location_id=loc.id,
            name=loc.name,
            latitude=loc.latitude,
            longitude=loc.longitude,
            risk_score=score,
            risk_level=level,
            rainfall_24h=75.0,
            soil_moisture=60.0,
            last_updated=latest.timestamp if latest else datetime.utcnow()
        ))
    return points


@router.get("/risk/heatmap", response_model=List[RiskHeatmapPoint])
def get_risk_heatmap(db: Session = Depends(get_db)):
    """Return points for MapLibre dynamic risk heatmap overlay."""
    return get_current_risk(db)
