#!/usr/bin/env python
"""
CLI entry point to execute the complete ML training pipeline.
Trains Susceptibility (RandomForest) and Risk (XGBoost) models on synthetic NER datasets.
"""
import sys
import os
from pathlib import Path

# Add project root and backend to sys.path
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(backend_dir))

from ml.train import train_and_save

if __name__ == "__main__":
    output_directory = os.path.join(os.path.dirname(__file__), "..", "data", "models")
    train_and_save(output_dir=output_directory)
    print("\nTraining completed successfully! Models and metadata are ready in data/models/.")
