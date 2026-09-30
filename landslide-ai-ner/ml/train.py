"""
Model training pipeline for the NER Landslide Risk System.

Trains two complementary models:
  1. Susceptibility model (RandomForest) – location-based spatial risk
  2. Risk model (XGBoost) – time-series / event-aware trigger risk

Both models address the severe class imbalance (~15% positive rate)
through class-weight balancing and threshold calibration.
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Any

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    classification_report
)
from xgboost import XGBClassifier

from ml.data_loader import LandslideDataLoader
from ml.preprocessing import LandslidePreprocessor
from ml.feature_engineering import engineer_features
from ml.model_registry import ModelRegistry

logger = logging.getLogger(__name__)

# ── Features used for susceptibility (static terrain, historical)
SUSCEPTIBILITY_FEATURES = [
    'slope', 'elevation', 'aspect', 'curvature', 'drainage_density',
    'land_cover_encoded', 'distance_to_road', 'distance_to_river',
    'previous_landslide', 'historical_susceptibility', 'ndvi',
    'slope_tan', 'terrain_instability', 'land_cover_risk',
    'drainage_efficiency', 'vegetation_stability', 'river_proximity_factor',
]

# ── Features used for risk model (includes dynamic weather + terrain)
RISK_FEATURES = [
    'slope', 'elevation', 'drainage_density', 'land_cover_encoded',
    'distance_to_road', 'distance_to_river', 'previous_landslide',
    'historical_susceptibility', 'ndvi', 'change_score',
    'rainfall_24h', 'rainfall_72h', 'soil_moisture',
    'slope_tan', 'terrain_instability', 'combined_rainfall',
    'antecedent_moisture_index', 'rainfall_intensity_ratio',
    'land_cover_risk', 'rainfall_slope_interaction',
    'drainage_efficiency', 'vegetation_stability', 'river_proximity_factor',
]


class ModelTrainer:
    """
    Trains susceptibility and risk classification models with
    cross-validation, class-imbalance handling, and full metric reporting.
    """

    def __init__(self, n_cv_folds: int = 5, random_state: int = 42):
        self.n_cv_folds   = n_cv_folds
        self.random_state = random_state

    # ─────────────────────────────────────────────────────────────────────────
    def train_susceptibility_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: list = None,
    ) -> RandomForestClassifier:
        """
        Train RandomForestClassifier for spatial susceptibility.

        Design choices:
        - n_estimators=200: sufficient ensemble diversity
        - max_depth=15: allows complex terrain interactions without full overfit
        - class_weight='balanced': auto-adjusts for ~15% positive class
        - min_samples_leaf=5: prevents overly specific leaves
        - StratifiedKFold ensures each fold has same class ratio
        """
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features='sqrt',
            class_weight='balanced',
            random_state=self.random_state,
            n_jobs=-1,
            oob_score=True,
        )

        logger.info("Training susceptibility model (RandomForest)…")
        cv = StratifiedKFold(n_splits=self.n_cv_folds, shuffle=True,
                             random_state=self.random_state)
        cv_scores = cross_val_score(model, X_train, y_train,
                                    cv=cv, scoring='roc_auc', n_jobs=-1)
        logger.info(
            f"  CV ROC-AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}"
        )

        model.fit(X_train, y_train)
        logger.info(f"  OOB score: {model.oob_score_:.4f}")

        # Store for later access
        model.cv_scores_    = cv_scores
        model.feature_names = feature_names or []
        return model

    # ─────────────────────────────────────────────────────────────────────────
    def train_risk_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray   = None,
        y_val: np.ndarray   = None,
        feature_names: list = None,
    ) -> XGBClassifier:
        """
        Train XGBClassifier for dynamic risk prediction (time-aware features).

        Design choices:
        - scale_pos_weight: handles class imbalance (ratio neg/pos)
        - early_stopping_rounds: prevents overfit
        - eval_metric='aucpr': optimises precision-recall, better for rare events
        - tree_method='hist': fast for medium datasets
        """
        n_neg          = int((y_train == 0).sum())
        n_pos          = int((y_train == 1).sum())
        scale_pos_weight = n_neg / max(n_pos, 1)
        logger.info(
            f"  Class ratio neg/pos = {scale_pos_weight:.2f} "
            f"(neg={n_neg}, pos={n_pos})"
        )

        # Use provided validation set or auto-split
        if X_val is None or y_val is None:
            X_train, X_val, y_train, y_val = train_test_split(
                X_train, y_train, test_size=0.15,
                stratify=y_train, random_state=self.random_state
            )

        model = XGBClassifier(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=5,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            scale_pos_weight=scale_pos_weight,
            eval_metric='aucpr',
            early_stopping_rounds=30,
            tree_method='hist',
            random_state=self.random_state,
            verbosity=0,
        )

        logger.info("Training risk model (XGBoost)…")
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )
        best_iter = model.best_iteration
        logger.info(f"  Best iteration: {best_iter}")

        # Cross-validate on full training data (no early stopping)
        cv_model = XGBClassifier(
            n_estimators=best_iter + 1,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=5,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            scale_pos_weight=scale_pos_weight,
            tree_method='hist',
            random_state=self.random_state,
            verbosity=0,
        )
        cv_full   = np.concatenate([X_train, X_val])
        y_cv_full = np.concatenate([y_train, y_val])
        cv = StratifiedKFold(n_splits=self.n_cv_folds, shuffle=True,
                             random_state=self.random_state)
        cv_scores = cross_val_score(cv_model, cv_full, y_cv_full,
                                    cv=cv, scoring='roc_auc', n_jobs=-1)
        logger.info(
            f"  CV ROC-AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}"
        )

        model.cv_scores_    = cv_scores
        model.feature_names = feature_names or []
        return model

    # ─────────────────────────────────────────────────────────────────────────
    def evaluate(
        self,
        model,
        X_test: np.ndarray,
        y_test: np.ndarray,
        threshold: float = 0.35,
    ) -> dict:
        """
        Comprehensive evaluation with emphasis on recall (missed disasters = fatal).

        threshold=0.35 rather than 0.5 → biases toward fewer false negatives.
        """
        proba = model.predict_proba(X_test)[:, 1]
        y_pred = (proba >= threshold).astype(int)

        acc    = accuracy_score(y_test, y_pred)
        prec   = precision_score(y_test, y_pred, zero_division=0)
        rec    = recall_score(y_test, y_pred, zero_division=0)
        f1     = f1_score(y_test, y_pred, zero_division=0)
        roc    = roc_auc_score(y_test, proba)
        pr_auc = average_precision_score(y_test, proba)
        cm     = confusion_matrix(y_test, y_pred).tolist()
        cr     = classification_report(y_test, y_pred,
                                       target_names=['No Landslide', 'Landslide'],
                                       zero_division=0)

        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

        metrics = {
            'threshold':     threshold,
            'accuracy':      round(acc, 4),
            'precision':     round(prec, 4),
            'recall':        round(rec, 4),          # ← most critical: missed disasters
            'f1_score':      round(f1, 4),
            'roc_auc':       round(roc, 4),
            'pr_auc':        round(pr_auc, 4),
            'confusion_matrix': cm,
            'true_positives':   int(tp),
            'false_positives':  int(fp),
            'true_negatives':   int(tn),
            'false_negatives':  int(fn),             # ← false negatives = missed disasters
            'miss_rate':        round(fn / max(fn + tp, 1), 4),
            'classification_report': cr,
        }

        # CV scores if available
        if hasattr(model, 'cv_scores_'):
            metrics['cv_roc_auc_mean'] = round(model.cv_scores_.mean(), 4)
            metrics['cv_roc_auc_std']  = round(model.cv_scores_.std(), 4)

        logger.info(
            f"\n  ┌─ Evaluation Results ───────────────────────────────\n"
            f"  │  Threshold : {threshold}\n"
            f"  │  Accuracy  : {acc:.4f}\n"
            f"  │  Precision : {prec:.4f}\n"
            f"  │  Recall    : {rec:.4f}  ← (missed disasters = 1 - recall)\n"
            f"  │  F1-Score  : {f1:.4f}\n"
            f"  │  ROC-AUC   : {roc:.4f}\n"
            f"  │  PR-AUC    : {pr_auc:.4f}\n"
            f"  │  FN (miss) : {fn}\n"
            f"  └────────────────────────────────────────────────────"
        )
        return metrics

    # ─────────────────────────────────────────────────────────────────────────
    def save_model(
        self,
        model,
        preprocessor: LandslidePreprocessor,
        path: str,
        model_name: str,
        version: str,
        metrics: dict,
    ) -> dict:
        """
        Save model + preprocessor bundle and a sidecar metadata JSON.
        Returns a dict suitable for model_registry entry.
        """
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        bundle = {
            'model':           model,
            'preprocessor':    preprocessor,
            'model_name':      model_name,
            'version':         version,
            'metrics':         metrics,
            'saved_at':        datetime.utcnow().isoformat(),
        }
        joblib.dump(bundle, p)
        logger.info(f"Model saved → {p}")

        # Sidecar JSON
        meta_path = p.with_suffix('.json')
        meta = {
            'model_name':  model_name,
            'version':     version,
            'algorithm':   type(model).__name__,
            'metrics':     {k: v for k, v in metrics.items()
                            if not isinstance(v, (list, dict))},
            'saved_at':    bundle['saved_at'],
            'file_path':   str(p),
        }
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
        logger.info(f"Metadata saved → {meta_path}")

        return meta


# ─────────────────────────────────────────────────────────────────────────────
def train_and_save(output_dir: str = "data/models") -> dict:
    """
    Full end-to-end training pipeline:
      1. Generate synthetic NER dataset
      2. Feature engineering
      3. Train / test split (stratified 80/20)
      4. Fit preprocessor
      5. Train susceptibility (RF) + risk (XGB) models
      6. Evaluate both
      7. Save to output_dir
      8. Register in model_registry.json

    Returns dict with paths and metrics for both models.
    """
    from ml.evaluate import ModelEvaluator  # local import to avoid circular

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S',
    )

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("\n" + "═" * 60)
    print("  NER LANDSLIDE RISK — MODEL TRAINING PIPELINE")
    print("═" * 60)

    # ── 1. Data ────────────────────────────────────────────────────────────
    print("\n[1/7] Generating synthetic NER dataset (n=2000)…")
    loader = LandslideDataLoader()
    df_raw = loader.generate_synthetic_dataset(n_samples=2000, seed=42)
    print(f"      Rows: {len(df_raw)} | Positive rate: {df_raw['landslide_occurred'].mean():.1%}")

    # ── 2. Feature engineering ─────────────────────────────────────────────
    print("[2/7] Engineering features…")
    df = engineer_features(df_raw)

    # Determine available feature columns
    susc_feats = [c for c in SUSCEPTIBILITY_FEATURES if c in df.columns]
    risk_feats = [c for c in RISK_FEATURES if c in df.columns]
    print(f"      Susceptibility features: {len(susc_feats)}")
    print(f"      Risk features          : {len(risk_feats)}")

    target = loader.TARGET_COLUMN
    X_susc = df[susc_feats]
    X_risk = df[risk_feats]
    y      = df[target].values

    # ── 3. Train/test split ────────────────────────────────────────────────
    print("[3/7] Splitting train/test (80/20, stratified)…")
    from sklearn.model_selection import train_test_split as tts

    Xs_tr, Xs_te, y_tr, y_te = tts(X_susc, y, test_size=0.20,
                                    stratify=y, random_state=42)
    Xr_tr, Xr_te, y_tr, y_te = tts(X_risk, y, test_size=0.20,
                                    stratify=y, random_state=42)

    # ── 4. Preprocessors ──────────────────────────────────────────────────
    print("[4/7] Fitting preprocessors…")
    pre_susc = LandslidePreprocessor(feature_columns=susc_feats)
    pre_risk = LandslidePreprocessor(feature_columns=risk_feats)

    Xs_tr_sc = pre_susc.fit_transform(Xs_tr)
    Xs_te_sc = pre_susc.transform(Xs_te)

    Xr_tr_sc = pre_risk.fit_transform(Xr_tr)
    Xr_te_sc = pre_risk.transform(Xr_te)

    # ── 5. Train models ────────────────────────────────────────────────────
    print("[5/7] Training models…")
    trainer = ModelTrainer(n_cv_folds=5)

    susc_model = trainer.train_susceptibility_model(Xs_tr_sc, y_tr, susc_feats)
    risk_model  = trainer.train_risk_model(Xr_tr_sc, y_tr, feature_names=risk_feats)

    # ── 6. Evaluate ────────────────────────────────────────────────────────
    print("[6/7] Evaluating models…")
    evaluator = ModelEvaluator()

    susc_metrics = trainer.evaluate(susc_model, Xs_te_sc, y_te)
    risk_metrics  = trainer.evaluate(risk_model,  Xr_te_sc, y_te)

    evaluator.full_evaluation(
        susc_model, Xs_te_sc, y_te,
        model_name='susceptibility',
        output_dir=str(out / 'plots'),
        feature_names=susc_feats,
    )
    evaluator.full_evaluation(
        risk_model, Xr_te_sc, y_te,
        model_name='risk',
        output_dir=str(out / 'plots'),
        feature_names=risk_feats,
    )

    # ── 7. Save models ─────────────────────────────────────────────────────
    print("[7/7] Saving models…")
    susc_path = out / 'susceptibility_v1.pkl'
    risk_path  = out / 'risk_v1.pkl'

    susc_entry = trainer.save_model(
        susc_model, pre_susc, str(susc_path),
        'susceptibility', 'v1', susc_metrics,
    )
    risk_entry = trainer.save_model(
        risk_model, pre_risk, str(risk_path),
        'risk', 'v1', risk_metrics,
    )

    # ── Register ───────────────────────────────────────────────────────────
    registry = ModelRegistry(str(out / 'registry.json'))
    registry.register(
        model_name='susceptibility', version='v1',
        algorithm='RandomForestClassifier',
        metrics={k: v for k, v in susc_metrics.items()
                 if not isinstance(v, (list, dict))},
        features=susc_feats,
        file_path=str(susc_path),
        dataset_version='synthetic_ner_v1',
    )
    registry.activate('susceptibility', 'v1')

    registry.register(
        model_name='risk', version='v1',
        algorithm='XGBClassifier',
        metrics={k: v for k, v in risk_metrics.items()
                 if not isinstance(v, (list, dict))},
        features=risk_feats,
        file_path=str(risk_path),
        dataset_version='synthetic_ner_v1',
    )
    registry.activate('risk', 'v1')

    # ── Print summary table ────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("  TRAINING COMPLETE — METRICS SUMMARY")
    print("═" * 60)
    header = f"{'Metric':<22} {'Susceptibility':>16} {'Risk (XGB)':>14}"
    print(header)
    print("─" * 60)
    for key in ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc', 'pr_auc']:
        sv = susc_metrics.get(key, float('nan'))
        rv = risk_metrics.get(key,  float('nan'))
        marker = " ⚠" if key == 'recall' else ""
        print(f"  {key:<20} {sv:>16.4f} {rv:>14.4f}{marker}")
    print("─" * 60)
    print(f"  ⚠  Recall is most critical: missed disasters = false negatives")
    print(f"\n  Models saved to: {out.resolve()}")
    print("═" * 60 + "\n")

    return {
        'susceptibility': {'path': str(susc_path), 'metrics': susc_metrics},
        'risk':           {'path': str(risk_path),  'metrics': risk_metrics},
    }
