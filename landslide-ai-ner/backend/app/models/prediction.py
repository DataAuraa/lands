"""
Prediction and ML Model registry database models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    risk_score = Column(Float, nullable=False)           # 0 to 100
    # Risk Level: 'LOW', 'MODERATE', 'HIGH', 'VERY_HIGH', 'CRITICAL'
    risk_level = Column(String(30), nullable=False, index=True)
    probability = Column(Float, nullable=False)          # 0.0 to 1.0
    model_version = Column(String(50), default="v1.0")
    confidence = Column(Float, default=0.85)             # 0.0 to 1.0
    prediction_horizon = Column(Integer, default=24)     # hours
    
    # Explainability payload: {"top_factors": [...], "shap_values": {...}, "narrative": "..."}
    explanation = Column(JSON, nullable=True)
    features_used = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="predictions")


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False, unique=True)
    algorithm = Column(String(50), default="RandomForest")
    training_date = Column(DateTime, default=datetime.utcnow)
    dataset_version = Column(String(50), default="v1.0")
    features = Column(JSON, nullable=False)
    # Metrics: {"accuracy": 0.89, "recall": 0.92, "precision": 0.86, "f1": 0.89, "roc_auc": 0.94}
    metrics = Column(JSON, nullable=False)
    file_location = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
