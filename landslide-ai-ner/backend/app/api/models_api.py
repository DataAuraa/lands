"""
Machine Learning Models Management API Router.
Enables listing model checkpoints, inspecting validation metrics, triggering retraining, and activating versions.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from ml.model_registry import ModelRegistry
from app.services.auth_service import require_roles

router = APIRouter(prefix="/models", tags=["Model Registry"])
registry = ModelRegistry()


@router.get("")
def list_models():
    """List all registered ML model versions and their validation metrics."""
    return registry.list_all()


@router.get("/active")
def get_active_models():
    """Return currently deployed susceptibility and risk model versions."""
    return {
        "susceptibility": registry.get_active("susceptibility"),
        "risk": registry.get_active("risk"),
    }


@router.post("/{model_name}/activate/{version}")
def activate_model(
    model_name: str,
    version: str,
    current_user=Depends(require_roles("admin"))
):
    """Admin: Switch active inference checkpoint."""
    success = registry.activate(model_name, version)
    if not success:
        raise HTTPException(status_code=404, detail=f"Model {model_name} version {version} not found")
    return {"status": "SUCCESS", "message": f"Activated {model_name} version {version}"}


@router.post("/train")
def trigger_training(current_user=Depends(require_roles("admin"))):
    """Admin: Trigger model retraining pipeline in background."""
    from ml.train import train_and_save
    try:
        res = train_and_save()
        return {
            "status": "COMPLETED",
            "message": "Retrained susceptibility (RandomForest) and dynamic risk (XGBoost) models.",
            "metrics": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
