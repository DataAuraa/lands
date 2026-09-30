"""
Model Registry for tracking and versioning trained ML models.
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class ModelRegistry:
    def __init__(self, registry_path: str = "data/models/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_registry()

    def _ensure_registry(self):
        if not self.registry_path.exists():
            default_data = {
                "active_models": {
                    "susceptibility": "v1",
                    "risk": "v1"
                },
                "models": []
            }
            self._save(default_data)

    def _load(self) -> Dict[str, Any]:
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"active_models": {}, "models": []}

    def _save(self, data: Dict[str, Any]):
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def register(
        self,
        model_name: str,
        version: str,
        algorithm: str,
        metrics: Dict[str, Any],
        features: List[str],
        file_path: str,
        dataset_version: str = "v1.0"
    ) -> Dict[str, Any]:
        data = self._load()
        entry = {
            "model_name": model_name,
            "version": version,
            "algorithm": algorithm,
            "metrics": metrics,
            "features": features,
            "file_path": file_path,
            "dataset_version": dataset_version,
            "registered_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        # Update or add
        data["models"] = [m for m in data["models"] if not (m["model_name"] == model_name and m["version"] == version)]
        data["models"].append(entry)
        data["active_models"][model_name] = version
        self._save(data)
        return entry

    def activate(self, model_name: str, version: str) -> bool:
        data = self._load()
        matched = False
        for m in data["models"]:
            if m["model_name"] == model_name:
                if m["version"] == version:
                    m["is_active"] = True
                    matched = True
                else:
                    m["is_active"] = False
        if matched:
            data["active_models"][model_name] = version
            self._save(data)
        return matched

    def get_active(self, model_name: str) -> Optional[Dict[str, Any]]:
        data = self._load()
        active_ver = data.get("active_models", {}).get(model_name)
        if not active_ver:
            return None
        for m in data.get("models", []):
            if m["model_name"] == model_name and m["version"] == active_ver:
                return m
        return None

    def list_all(self) -> List[Dict[str, Any]]:
        data = self._load()
        return data.get("models", [])
