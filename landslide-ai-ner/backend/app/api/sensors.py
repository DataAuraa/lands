"""
Sensors and IoT Telemetry API Router.
Handles sensor registration, query, and high-frequency geotechnical telemetry ingestion.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sensor import SoilSensor, SoilSensorData
from app.models.location import Location
from app.schemas.sensor import SoilSensorCreate, SoilSensorResponse, SensorDataCreate, SensorDataResponse
from app.services.sensor_service import sensor_adapter
from app.services.auth_service import require_roles

router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.get("", response_model=List[SoilSensorResponse])
def list_sensors(
    location_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
):
    """List all deployed geotechnical IoT sensors with their latest battery and moisture values."""
    query = db.query(SoilSensor).filter(SoilSensor.is_active == True)
    if location_id:
        query = query.filter(SoilSensor.location_id == location_id)

    sensors = query.all()
    results = []
    for s in sensors:
        latest = (
            db.query(SoilSensorData)
            .filter(SoilSensorData.sensor_id == s.sensor_id)
            .order_by(SoilSensorData.timestamp.desc())
            .first()
        )
        res = SoilSensorResponse.model_validate(s)
        if latest:
            res.latest_soil_moisture = latest.soil_moisture
            res.latest_status = latest.sensor_status
            res.latest_battery = latest.battery_level
            res.last_seen = latest.timestamp
        else:
            res.latest_status = "ONLINE"
            res.latest_battery = 100.0

        if status_filter and res.latest_status != status_filter:
            continue
        results.append(res)

    return results


@router.get("/{sensor_id}", response_model=SoilSensorResponse)
def get_sensor(sensor_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed state of a single IoT node."""
    sensor = db.query(SoilSensor).filter(SoilSensor.sensor_id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    latest = (
        db.query(SoilSensorData)
        .filter(SoilSensorData.sensor_id == sensor.sensor_id)
        .order_by(SoilSensorData.timestamp.desc())
        .first()
    )
    res = SoilSensorResponse.model_validate(sensor)
    if latest:
        res.latest_soil_moisture = latest.soil_moisture
        res.latest_status = latest.sensor_status
        res.latest_battery = latest.battery_level
        res.last_seen = latest.timestamp
    return res


@router.post("/data", response_model=SensorDataResponse, status_code=status.HTTP_201_CREATED)
def post_sensor_telemetry(payload: SensorDataCreate, db: Session = Depends(get_db)):
    """
    Ingest real-time packet from ESP32/LoRaWAN field gateway.
    Stores reading and triggers geotechnical risk recalculation.
    """
    sensor = db.query(SoilSensor).filter(SoilSensor.sensor_id == payload.sensor_id).first()
    loc_id = payload.location_id or (sensor.location_id if sensor else 1)

    packet = payload.model_dump()
    packet["location_id"] = loc_id

    reading = sensor_adapter.ingest_reading(db, packet)
    return reading
