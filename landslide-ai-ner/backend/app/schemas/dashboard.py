"""
Pydantic schemas for Command Center Dashboard summaries and telemetry charts.
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from app.schemas.alert import AlertResponse
from app.schemas.report import FieldReportResponse


class DashboardSummary(BaseModel):
    total_locations: int
    active_sensors: int
    sensors_online: int
    sensors_offline: int
    sensors_warning: int
    
    # Risk counts
    low_risk_count: int
    moderate_risk_count: int
    high_risk_count: int
    very_high_risk_count: int
    critical_risk_count: int
    
    active_alerts: int
    open_incidents: int
    blocked_roads: int
    
    risk_distribution: Dict[str, int]
    system_status: Dict[str, str]
    
    recent_alerts: List[AlertResponse]
    recent_reports: List[FieldReportResponse]
    
    simulation_mode: bool
    model_version: str
    last_updated: datetime


class RiskTrendPoint(BaseModel):
    timestamp: datetime
    average_risk: float
    max_risk: float
    critical_zones: int


class RainfallTrendPoint(BaseModel):
    timestamp: datetime
    rainfall_1h: float
    rainfall_24h: float
    temperature: float


class AlertTimelinePoint(BaseModel):
    timestamp: datetime
    alert_count: int
    highest_severity: str
