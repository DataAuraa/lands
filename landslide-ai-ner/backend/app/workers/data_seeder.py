"""
Database Seeder for Northeast India (NER) Landslide Monitoring Prototype.
Populates admin users, 12 monitored geozones, IoT sensor nodes, historical disaster inventory,
and initial telemetry. Fully idempotent.
"""
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.models.user import User
from app.models.location import Location
from app.models.sensor import SoilSensor, SoilSensorData
from app.models.terrain import TerrainData
from app.models.weather import WeatherData
from app.models.landslide import HistoricalLandslide
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.field_report import FieldReport
from app.services.auth_service import get_password_hash

logger = logging.getLogger(__name__)


def seed_database():
    """Seed initial data into database if empty."""
    init_db()
    db: Session = SessionLocal()
    try:
        # 1. Seed Users
        if db.query(User).count() == 0:
            logger.info("Seeding default demonstration users...")
            users = [
                User(
                    name="State Disaster Admin",
                    email="admin@landslide-ner.gov.in",
                    phone="+91-361-2237001",
                    password_hash=get_password_hash("Admin@1234"),
                    role="admin",
                    district="Kamrup Metro",
                    state="Assam",
                    preferred_language="en",
                    is_active=True
                ),
                User(
                    name="Noney DEOC District Officer",
                    email="district@landslide-ner.gov.in",
                    phone="+91-387-2234002",
                    password_hash=get_password_hash("District@1234"),
                    role="district_admin",
                    district="Noney",
                    state="Manipur",
                    preferred_language="en",
                    is_active=True
                ),
                User(
                    name="Field Patrol Officer Rongmei",
                    email="officer@landslide-ner.gov.in",
                    phone="+91-943-5567890",
                    password_hash=get_password_hash("Officer@1234"),
                    role="field_officer",
                    district="Noney",
                    state="Manipur",
                    preferred_language="en",
                    is_active=True
                ),
                User(
                    name="Citizen Observer",
                    email="citizen@landslide-ner.gov.in",
                    phone="+91-986-2123456",
                    password_hash=get_password_hash("Citizen@1234"),
                    role="citizen",
                    district="Kohima",
                    state="Nagaland",
                    preferred_language="en",
                    is_active=True
                )
            ]
            db.add_all(users)
            db.commit()
            logger.info("Users seeded successfully.")

        # 2. Seed Locations from data/raw/ner_locations.json
        if db.query(Location).count() == 0:
            logger.info("Seeding monitored NER locations...")
            raw_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw" / "ner_locations.json"
            if raw_path.exists():
                with open(raw_path, "r", encoding="utf-8") as f:
                    loc_data = json.load(f)
                
                for item in loc_data:
                    loc = Location(
                        id=item["id"],
                        name=item["name"],
                        state=item["state"],
                        district=item["district"],
                        block=item.get("block"),
                        village=item.get("village"),
                        latitude=item["latitude"],
                        longitude=item["longitude"],
                        elevation=item.get("elevation", 500.0),
                        population=item.get("population", 1000),
                        road_connectivity=item.get("road_connectivity", "paved"),
                        infrastructure_type=item.get("infrastructure_type", "residential"),
                        slope=item.get("slope", 25.0),
                        aspect=item.get("aspect", 180.0),
                        land_cover=item.get("land_cover", "mixed_forest"),
                        geology=item.get("geology", "sedimentary"),
                        distance_to_road=item.get("distance_to_road", 0.5),
                        distance_to_river=item.get("distance_to_river", 1.0),
                        is_active=True
                    )
                    db.add(loc)

                    # Associated TerrainData
                    terrain = TerrainData(
                        location_id=item["id"],
                        elevation=item.get("elevation", 500.0),
                        slope=item.get("slope", 25.0),
                        aspect=item.get("aspect", 180.0),
                        curvature=0.15,
                        drainage_density=1.8,
                        terrain_ruggedness=24.5,
                        land_cover=item.get("land_cover", "mixed_forest"),
                        geology=item.get("geology", "sedimentary"),
                        distance_to_road=item.get("distance_to_road", 0.5),
                        distance_to_river=item.get("distance_to_river", 1.0),
                    )
                    db.add(terrain)

                    # Associated IoT Soil Sensor
                    sensor = SoilSensor(
                        sensor_id=f"SOIL_NODE_{item['id']:03d}",
                        location_id=item["id"],
                        name=f"{item['name']} Slope Sensor",
                        latitude=item["latitude"] + 0.001,
                        longitude=item["longitude"] + 0.001,
                        is_active=True
                    )
                    db.add(sensor)

                    # Initial Soil Moisture Reading
                    moisture_val = 78.0 if item["id"] == 2 else (65.0 if item["id"] in [1, 7, 10] else 42.0)
                    reading = SoilSensorData(
                        sensor_id=f"SOIL_NODE_{item['id']:03d}",
                        location_id=item["id"],
                        timestamp=datetime.utcnow(),
                        soil_moisture=moisture_val,
                        soil_temperature=21.5,
                        soil_pressure=101.4 + (moisture_val / 15.0),
                        battery_level=96.0,
                        sensor_status="ONLINE"
                    )
                    db.add(reading)

                    # Initial Weather Record
                    rf_24 = 185.0 if item["id"] == 2 else (110.0 if item["id"] in [1, 7] else 35.0)
                    w = WeatherData(
                        station_id=f"AWS_{item['id']}",
                        latitude=item["latitude"],
                        longitude=item["longitude"],
                        timestamp=datetime.utcnow(),
                        rainfall_1h=round(rf_24 * 0.12, 1),
                        rainfall_3h=round(rf_24 * 0.3, 1),
                        rainfall_6h=round(rf_24 * 0.5, 1),
                        rainfall_12h=round(rf_24 * 0.8, 1),
                        rainfall_24h=rf_24,
                        rainfall_72h=round(rf_24 * 1.8, 1),
                        temperature=22.0,
                        humidity=85.0,
                        wind_speed=14.0,
                        pressure=1005.0,
                        source="DEMO"
                    )
                    db.add(w)

                    # Initial Prediction
                    risk_score = 84.0 if item["id"] == 2 else (62.0 if item["id"] in [1, 7] else 24.0)
                    risk_level = "CRITICAL" if risk_score >= 81 else ("HIGH" if risk_score >= 41 else "LOW")
                    pred = Prediction(
                        location_id=item["id"],
                        timestamp=datetime.utcnow(),
                        risk_score=risk_score,
                        risk_level=risk_level,
                        probability=round(risk_score / 100.0, 3),
                        model_version="v1.0-RF-XGB",
                        confidence=0.87,
                        prediction_horizon=24,
                        explanation={"top_factors": [
                            f"Accumulated 24h rainfall: {rf_24} mm",
                            f"Soil moisture saturation: {moisture_val}%",
                            f"Steep slope angle: {item.get('slope')}°"
                        ]},
                        features_used={"rainfall_24h": rf_24, "soil_moisture": moisture_val}
                    )
                    db.add(pred)

                db.commit()
                logger.info(f"Seeded {len(loc_data)} locations, sensors, and predictions.")

        # 3. Seed Historical Landslides
        if db.query(HistoricalLandslide).count() == 0:
            hist_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw" / "historical_landslides.json"
            if hist_path.exists():
                with open(hist_path, "r", encoding="utf-8") as f:
                    hist_data = json.load(f)
                for h in hist_data:
                    ev = HistoricalLandslide(
                        id=h["id"],
                        location_id=h.get("location_id"),
                        event_date=datetime.fromisoformat(h["event_date"]),
                        latitude=h["latitude"],
                        longitude=h["longitude"],
                        severity=h["severity"],
                        rainfall_before_event=h.get("rainfall_before_event", 100.0),
                        estimated_damage=h.get("estimated_damage", 50.0),
                        road_blocked=h.get("road_blocked", False),
                        casualties=h.get("casualties", 0),
                        source=h.get("source", "State DMA"),
                        description=h.get("description", "")
                    )
                    db.add(ev)
                db.commit()
                logger.info(f"Seeded {len(hist_data)} historical landslide incidents.")

        # 4. Seed Active Alerts
        if db.query(Alert).count() == 0:
            alert = Alert(
                location_id=2,  # Noney Tupul
                alert_type="AUTOMATED_RISK_TRIGGER",
                risk_level="CRITICAL",
                message="CRITICAL landslide risk indication detected near Noney Tupul Yard. High saturation of slope crown. Follow instructions from local authorities immediately.\n\n[This is an AI-generated risk indication. Follow official disaster management guidance.]",
                language="en",
                created_at=datetime.utcnow() - timedelta(minutes=25),
                expires_at=datetime.utcnow() + timedelta(hours=6),
                delivery_status="SENT",
                recipient_count=1500,
                is_active=True
            )
            db.add(alert)
            db.commit()

        # 5. Seed Initial Field Report
        if db.query(FieldReport).count() == 0:
            report = FieldReport(
                user_id=3,  # Officer Rongmei
                location_id=2,
                latitude=24.9235,
                longitude=93.5985,
                report_type="Crack",
                description="12cm wide tension crack detected along upper railway yard cutting following 180mm continuous rainfall.",
                severity="critical",
                timestamp=datetime.utcnow() - timedelta(minutes=40),
                verification_status="VERIFIED",
                verified_by=1,
                verified_at=datetime.utcnow() - timedelta(minutes=15)
            )
            db.add(report)
            db.commit()

        logger.info("Database seeding complete!")
    except Exception as e:
        logger.error(f"Error during database seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
