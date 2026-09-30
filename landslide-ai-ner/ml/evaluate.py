"""
Model evaluation utilities: metrics, ROC/PR curves, confusion matrix,
and feature importance plots for the NER Landslide Risk System.
"""
import os
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')   # non-interactive backend — safe for server/notebook
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score,
    roc_curve, precision_recall_curve,
    confusion_matrix, ConfusionMatrixDisplay,
    classification_report,
)

logger = logging.getLogger(__name__)

FEATURE_DESCRIPTIONS = {
    'rainfall_24h':              '24-hr rainfall (mm)',
    'rainfall_72h':              '72-hr rainfall (mm)',
    'soil_moisture':             'Soil moisture (%)',
    'slope':                     'Terrain slope (°)',
    'elevation':                 'Elevation (m)',
    'historical_susceptibility': 'Historical susceptibility',
    'change_score':              'Satellite change score',
    'ndvi':                      'Vegetation index (NDVI)',
    'distance_to_road':          'Distance to road (km)',
    'distance_to_river':         'Distance to river (km)',
    'drainage_density':          'Drainage density',
    'combined_rainfall':         'Weighted antecedent rainfall',
    'terrain_instability':       'Terrain instability index',
    'slope_tan':                 'Slope tangent',
    'antecedent_moisture_index': 'Antecedent moisture index',
    'land_cover_risk':           'Land-cover risk coefficient',
    'rainfall_slope_interaction':'Rainfall × slope interaction',
    'drainage_efficiency':       'Drainage efficiency index',
    'vegetation_stability':      'Vegetation stability',
    'river_proximity_factor':    'River proximity factor',
    'rainfall_intensity_ratio':  'Rainfall intensity ratio',
}

PLOT_STYLE = {
    'figure.dpi':        150,
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'font.size':         11,
}


class ModelEvaluator:
    """
    Generates comprehensive evaluation artefacts for a trained classifier:
    - Scalar metrics
    - ROC curve
    - Precision-Recall curve
    - Confusion matrix
    - Feature importance (sorted bar chart)
    """

    def full_evaluation(
        self,
        model,
        X_test:       np.ndarray,
        y_test:       np.ndarray,
        model_name:   str,
        output_dir:   str = 'data/models/plots',
        feature_names: list = None,
        threshold:    float = 0.35,
    ) -> dict:
        """
        Run full evaluation and save all plots to output_dir.

        Returns
        -------
        dict with keys: metrics, plot_paths, classification_report
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        proba  = model.predict_proba(X_test)[:, 1]
        y_pred = (proba >= threshold).astype(int)

        metrics = self._compute_metrics(y_test, y_pred, proba, threshold)

        plots = {}
        plots['roc_curve']        = self._plot_roc(proba, y_test, model_name, out)
        plots['pr_curve']         = self._plot_pr(proba, y_test, model_name, out)
        plots['confusion_matrix'] = self._plot_cm(y_test, y_pred, model_name, out, threshold)

        if feature_names:
            fi = self.get_feature_importance(model, feature_names)
            plots['feature_importance'] = self._plot_importance(fi, model_name, out)
        else:
            fi = []

        cr = classification_report(
            y_test, y_pred,
            target_names=['No Landslide', 'Landslide'],
            zero_division=0,
        )
        logger.info(f"\nClassification Report ({model_name}):\n{cr}")

        return {
            'model_name':            model_name,
            'metrics':               metrics,
            'plot_paths':            plots,
            'feature_importance':    fi,
            'classification_report': cr,
        }

    # ─────────────────────────────────────────────────────────────────────────
    def get_feature_importance(self, model, feature_names: list) -> list:
        """
        Extract and sort feature importances.

        Supports RandomForest (.feature_importances_) and XGBoost
        (.feature_importances_ or .get_booster().get_score()).

        Returns list of dicts: [{feature, importance, description}]
        """
        importances = None

        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'get_booster'):
            try:
                score = model.get_booster().get_score(importance_type='gain')
                importances = np.array([score.get(f'f{i}', 0.0)
                                        for i in range(len(feature_names))])
                total = importances.sum() or 1.0
                importances = importances / total
            except Exception:
                importances = np.ones(len(feature_names)) / len(feature_names)

        if importances is None or len(importances) != len(feature_names):
            importances = np.ones(len(feature_names)) / len(feature_names)

        result = [
            {
                'feature':     name,
                'importance':  round(float(imp), 5),
                'description': FEATURE_DESCRIPTIONS.get(name, name.replace('_', ' ').title()),
            }
            for name, imp in zip(feature_names, importances)
        ]
        result.sort(key=lambda x: x['importance'], reverse=True)
        return result

    # ─────────────────────────────────────────────────────────────────────────
    def _compute_metrics(self, y_true, y_pred, proba, threshold) -> dict:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        return {
            'threshold':   threshold,
            'accuracy':    round(accuracy_score(y_true, y_pred), 4),
            'precision':   round(precision_score(y_true, y_pred, zero_division=0), 4),
            'recall':      round(recall_score(y_true, y_pred, zero_division=0), 4),
            'f1_score':    round(f1_score(y_true, y_pred, zero_division=0), 4),
            'roc_auc':     round(roc_auc_score(y_true, proba), 4),
            'pr_auc':      round(average_precision_score(y_true, proba), 4),
            'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn),
            'miss_rate':   round(fn / max(fn + tp, 1), 4),
        }

    # ─────────────────────────────────────────────────────────────────────────
    def _plot_roc(self, proba, y_true, model_name: str, out: Path) -> str:
        fpr, tpr, _ = roc_curve(y_true, proba)
        auc          = roc_auc_score(y_true, proba)

        with plt.rc_context(PLOT_STYLE):
            fig, ax = plt.subplots(figsize=(7, 6))
            ax.plot(fpr, tpr, lw=2, color='#E74C3C',
                    label=f'ROC AUC = {auc:.4f}')
            ax.plot([0, 1], [0, 1], '--', color='grey', lw=1, label='Random')
            ax.fill_between(fpr, tpr, alpha=0.12, color='#E74C3C')
            ax.set_xlabel('False Positive Rate')
            ax.set_ylabel('True Positive Rate (Recall)')
            ax.set_title(f'ROC Curve — {model_name.title()} Model')
            ax.legend(loc='lower right')
            ax.grid(True, alpha=0.3)
            path = out / f'roc_{model_name}.png'
            fig.tight_layout()
            fig.savefig(path)
            plt.close(fig)
        logger.info(f"  Saved ROC curve → {path}")
        return str(path)

    def _plot_pr(self, proba, y_true, model_name: str, out: Path) -> str:
        prec, rec, _ = precision_recall_curve(y_true, proba)
        pr_auc        = average_precision_score(y_true, proba)
        baseline      = y_true.mean()

        with plt.rc_context(PLOT_STYLE):
            fig, ax = plt.subplots(figsize=(7, 6))
            ax.plot(rec, prec, lw=2, color='#2980B9',
                    label=f'PR AUC = {pr_auc:.4f}')
            ax.axhline(baseline, linestyle='--', color='grey', lw=1,
                       label=f'Baseline (pos rate={baseline:.2f})')
            ax.fill_between(rec, prec, alpha=0.12, color='#2980B9')
            ax.set_xlabel('Recall')
            ax.set_ylabel('Precision')
            ax.set_title(f'Precision-Recall Curve — {model_name.title()} Model')
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)
            path = out / f'pr_{model_name}.png'
            fig.tight_layout()
            fig.savefig(path)
            plt.close(fig)
        logger.info(f"  Saved PR curve → {path}")
        return str(path)

    def _plot_cm(self, y_true, y_pred, model_name: str,
                 out: Path, threshold: float) -> str:
        cm   = confusion_matrix(y_true, y_pred)
        disp = ConfusionMatrixDisplay(cm, display_labels=['No Landslide', 'Landslide'])

        with plt.rc_context(PLOT_STYLE):
            fig, ax = plt.subplots(figsize=(6, 5))
            disp.plot(ax=ax, colorbar=False, cmap='Blues')
            ax.set_title(
                f'Confusion Matrix — {model_name.title()} Model\n'
                f'(threshold={threshold})'
            )
            tn, fp, fn, tp = cm.ravel()
            ax.text(0.98, 0.02,
                    f'FN (missed disasters) = {fn}',
                    transform=ax.transAxes,
                    ha='right', va='bottom',
                    fontsize=9, color='#C0392B',
                    bbox=dict(boxstyle='round', facecolor='#FADBD8', alpha=0.8))
            path = out / f'cm_{model_name}.png'
            fig.tight_layout()
            fig.savefig(path)
            plt.close(fig)
        logger.info(f"  Saved confusion matrix → {path}")
        return str(path)

    def _plot_importance(self, fi: list, model_name: str, out: Path) -> str:
        top_n = min(15, len(fi))
        top   = fi[:top_n]

        names  = [d['feature'] for d in top]
        values = [d['importance'] for d in top]
        descs  = [d['description'] for d in top]

        colors = cm.RdYlGn_r(np.linspace(0.1, 0.85, len(names)))

        with plt.rc_context(PLOT_STYLE):
            fig, ax = plt.subplots(figsize=(9, max(5, top_n * 0.45)))
            bars = ax.barh(range(len(names)), values[::-1],
                           color=colors[::-1], edgecolor='white', height=0.7)
            ax.set_yticks(range(len(names)))
            ax.set_yticklabels([descs[i] for i in range(len(names) - 1, -1, -1)],
                               fontsize=9)
            ax.set_xlabel('Feature Importance')
            ax.set_title(f'Top-{top_n} Feature Importances — {model_name.title()} Model')
            ax.grid(axis='x', alpha=0.3)
            for i, bar in enumerate(bars):
                ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height() / 2,
                        f'{values[top_n - 1 - i]:.4f}',
                        va='center', fontsize=8)
            path = out / f'importance_{model_name}.png'
            fig.tight_layout()
            fig.savefig(path)
            plt.close(fig)
        logger.info(f"  Saved feature importance → {path}")
        return str(path)
