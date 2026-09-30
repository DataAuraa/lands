"""
Models initialization module exporting all database tables.
"""
from app.models.user import User
from app.models.location import Location
from app.models.weather import WeatherData
from app.models.sensor import SoilSensor, SoilSensorData
from app.models.terrain import TerrainData
from app.models.satellite import SatelliteData
from app.models.landslide import HistoricalLandslide
from app.models.prediction import Prediction, MLModel
from app.models.alert import Alert
from app.models.field_report import FieldReport
from app.models.audit_log import AuditLog

__all__ = [
    "User",
    "Location",
    "WeatherData",
    "SoilSensor",
    "SoilSensorData",
    "TerrainData",
    "SatelliteData",
    "HistoricalLandslide",
    "Prediction",
    "MLModel",
    "Alert",
    "FieldReport",
    "AuditLog",
]
