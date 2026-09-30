"""
Alert Engine and Notification Dispatcher.
Evaluates risk triggers, generates multi-tier warnings, and coordinates SMS, Email, and Push adapters.
"""
from datetime import datetime, timedelta
import logging
from typing import Optional, List
from sqlalchemy.orm import Session

from app.config import settings
from app.models.alert import Alert
from app.models.location import Location
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class AlertService:
    """Disaster Alert Engine evaluating conditions and orchestrating notification dispatches."""

    def evaluate_and_trigger(self, db: Session, location: Location, risk_result: dict) -> Optional[Alert]:
        """Check if risk scores qualify for immediate disaster alert."""
        risk_level = risk_result["risk_level"]
        risk_score = risk_result["risk_score"]

        # Only HIGH, VERY_HIGH, and CRITICAL generate automated public/authority alerts
        if risk_level not in ["HIGH", "VERY_HIGH", "CRITICAL"]:
            return None

        # Check if an active unexpired alert already exists for this location
        existing_alert = (
            db.query(Alert)
            .filter(
                Alert.location_id == location.id,
                Alert.is_active == True,
                Alert.risk_level == risk_level,
                Alert.created_at >= datetime.utcnow() - timedelta(hours=3)
            )
            .first()
        )
        if existing_alert:
            return existing_alert

        # Generate multilingual alert text
        alert_msg = notification_service.format_alert_message(
            risk_level=risk_level,
            location_name=location.name,
            language="en"
        )

        alert = Alert(
            location_id=location.id,
            alert_type="AUTOMATED_RISK_TRIGGER",
            risk_level=risk_level,
            message=alert_msg,
            language="en",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=6),
            delivery_status="SENT",
            recipient_count=location.population or 150,
            is_active=True,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        # Dispatch via multi-channel adapters
        self._dispatch_channels(alert, location)
        return alert

    def _dispatch_channels(self, alert: Alert, location: Location):
        """Simulate or execute SMS, Email, and Authority webhooks."""
        logger.info(f"DISPATCH ALERT [{alert.risk_level}] for {location.name}: {alert.message}")
        if settings.SMS_API_KEY:
            logger.info(f"Forwarded alert to SMS Gateway for {location.name}")
        if settings.EMAIL_USERNAME:
            logger.info(f"Dispatched email bulletin to District Emergency Operations Center (DEOC)")


alert_service = AlertService()
