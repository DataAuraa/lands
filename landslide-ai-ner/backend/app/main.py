"""
Main FastAPI Application Entrypoint.
Provides REST APIs, real-time WebSocket multiplexing, and auto-seeding on startup.
"""
from contextlib import asynccontextmanager
from datetime import datetime
import json
import logging
import os
from typing import List, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.workers.data_seeder import seed_database
from app.api import (
    auth_router,
    users_router,
    locations_router,
    weather_router,
    sensors_router,
    predictions_router,
    alerts_router,
    reports_router,
    dashboard_router,
    gis_router,
    satellite_router,
    landslides_router,
    models_router,
    simulation_router,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── WebSocket Real-time Connection Manager ────────────────────────────────────
class ConnectionManager:
    """Manages active WebSockets for real-time telemetry and hazard alerts."""

    def __init__(self):
        self.dashboard_sockets: List[WebSocket] = []
        self.alert_sockets: List[WebSocket] = []
        self.sensor_sockets: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel == "dashboard":
            self.dashboard_sockets.append(websocket)
        elif channel == "alerts":
            self.alert_sockets.append(websocket)
        elif channel == "sensors":
            self.sensor_sockets.append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel == "dashboard" and websocket in self.dashboard_sockets:
            self.dashboard_sockets.remove(websocket)
        elif channel == "alerts" and websocket in self.alert_sockets:
            self.alert_sockets.remove(websocket)
        elif channel == "sensors" and websocket in self.sensor_sockets:
            self.sensor_sockets.remove(websocket)

    async def broadcast(self, channel: str, message: Dict[str, Any]):
        """Broadcast payload across subscribers of channel."""
        targets = []
        if channel == "dashboard":
            targets = list(self.dashboard_sockets)
        elif channel == "alerts":
            targets = list(self.alert_sockets)
        elif channel == "sensors":
            targets = list(self.sensor_sockets)

        dead_sockets = []
        for ws in targets:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead_sockets.append(ws)

        for dead in dead_sockets:
            self.disconnect(dead, channel)


ws_manager = ConnectionManager()


# ── App Lifespan Management ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB schema & seed initial demonstration records
    logger.info("Initializing Landslide AI NER Database and Seeding...")
    try:
        init_db()
        seed_database()
    except Exception as e:
        logger.error(f"Startup initialization error: {e}")

    # Ensure media directory exists for file uploads
    media_dir = os.path.join(os.path.dirname(__file__), "..", settings.MEDIA_DIR)
    os.makedirs(media_dir, exist_ok=True)

    yield
    logger.info("Shutting down Landslide AI NER System...")


# ── Application Factory ──────────────────────────────────────────────────────
app = FastAPI(
    title="AI-Based Early Warning & Landslide Risk Monitoring System (NER)",
    description=(
        "Production-oriented decision-support and geotechnical monitoring platform "
        "calibrated for the North Eastern Region (NER) of India.\n\n"
        "Integrates high-frequency rainfall telemetry, soil pore pressure sensor streams, "
        "terrain geomechanics, satellite deformation indices, and Explainable AI (XAI)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local media directory for file uploads
media_path = os.path.join(os.path.dirname(__file__), "..", settings.MEDIA_DIR)
os.makedirs(media_path, exist_ok=True)
app.mount("/media", StaticFiles(directory=media_path), name="media")

# ── Include REST Routers ─────────────────────────────────────────────────────
api_prefix = "/api"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(users_router, prefix=api_prefix)
app.include_router(locations_router, prefix=api_prefix)
app.include_router(weather_router, prefix=api_prefix)
app.include_router(sensors_router, prefix=api_prefix)
app.include_router(predictions_router, prefix=api_prefix)
app.include_router(alerts_router, prefix=api_prefix)
app.include_router(reports_router, prefix=api_prefix)
app.include_router(dashboard_router, prefix=api_prefix)
app.include_router(gis_router, prefix=api_prefix)
app.include_router(satellite_router, prefix=api_prefix)
app.include_router(landslides_router, prefix=api_prefix)
app.include_router(models_router, prefix=api_prefix)
app.include_router(simulation_router, prefix=api_prefix)


# ── System Health Endpoint ───────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    """System health and component status check."""
    return {
        "status": "HEALTHY",
        "app_name": settings.APP_NAME,
        "simulation_mode": settings.SIMULATION_MODE,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "region": "North Eastern Region (NER), India"
    }


# ── Real-Time WebSockets ─────────────────────────────────────────────────────
@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """Real-time push channel for dashboard cards, rainfall surges, and risk updates."""
    await ws_manager.connect(websocket, "dashboard")
    try:
        while True:
            # Echo or process incoming ping/events
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"event": "pong"}))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "dashboard")


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """Urgent push channel for automated disaster warnings and emergency bulletins."""
    await ws_manager.connect(websocket, "alerts")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "alerts")


@app.websocket("/ws/sensors")
async def websocket_sensors(websocket: WebSocket):
    """High-frequency telemetry stream for IoT soil moisture nodes."""
    await ws_manager.connect(websocket, "sensors")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "sensors")
