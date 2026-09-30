"""
API Package router collection.
"""
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.locations import router as locations_router
from app.api.weather import router as weather_router
from app.api.sensors import router as sensors_router
from app.api.predictions import router as predictions_router
from app.api.alerts import router as alerts_router
from app.api.reports import router as reports_router
from app.api.dashboard import router as dashboard_router
from app.api.gis import router as gis_router
from app.api.satellite import router as satellite_router
from app.api.landslides import router as landslides_router
from app.api.models_api import router as models_router
from app.api.simulation_api import router as simulation_router

__all__ = [
    "auth_router",
    "users_router",
    "locations_router",
    "weather_router",
    "sensors_router",
    "predictions_router",
    "alerts_router",
    "reports_router",
    "dashboard_router",
    "gis_router",
    "satellite_router",
    "landslides_router",
    "models_router",
    "simulation_router",
]
