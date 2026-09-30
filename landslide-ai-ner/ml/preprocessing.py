"""
Preprocessing pipeline for landslide ML features.
Handles missing values, categorical encoding, scaling, and data validation.
"""
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import logging

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    'slope', 'elevation', 'aspect', 'curvature', 'drainage_density',
    'rainfall_24h', 'rainfall_72h', 'soil_moisture', 'land_cover_encoded',
    'distance_to_road', 'distance_to_river', 'previous_landslide',
    'historical_susceptibility', 'ndvi', 'change_score'
]

# NER-calibrated valid ranges for outlier detection
VALID_RANGES = {
    'slope':                     (0,   90),
    'elevation':                 (50,  4000),
    'aspect':                    (0,   360),
    'curvature':                 (-10, 10),
    'drainage_density':          (0,   15),
    'rainfall_24h':              (0,   600),
    'rainfall_72h':              (0,   1500),
    'soil_moisture':             (0,   100),
    'land_cover_encoded':        (0,   9),
    'distance_to_road':          (0,   50),
    'distance_to_river':         (0,   50),
    'previous_landslide':        (0,   1),
    'historical_susceptibility': (0,   1),
    'ndvi':                      (-1,  1),
    'change_score':              (0,   1),
}


class LandslidePreprocessor:
    """
    Sklearn-compatible preprocessor that fits imputers and scalers on training data
    and applies consistent transforms at inference time.
    """

    def __init__(self, feature_columns: list = None):
        self.feature_columns = feature_columns or FEATURE_COLUMNS
        self.imputer = SimpleImputer(strategy='median')
        self.scaler  = StandardScaler()
        self._fitted  = False

    # ─────────────────────────────────────────────────────────────────────────
    def fit(self, X: pd.DataFrame, y=None) -> 'LandslidePreprocessor':
        """Fit imputer and scaler on training data."""
        Xf = self._select_features(X)
        Xf = self._clip_extremes(Xf)
        self.imputer.fit(Xf)
        X_imp = self.imputer.transform(Xf)
        self.scaler.fit(X_imp)
        self._fitted = True
        logger.info(f"Preprocessor fitted on {Xf.shape[0]} samples, {Xf.shape[1]} features.")
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Apply imputation and scaling. Preprocessor must be fitted first."""
        if not self._fitted:
            raise RuntimeError("LandslidePreprocessor.fit() must be called before transform().")
        Xf = self._select_features(X)
        Xf = self._clip_extremes(Xf)
        X_imp   = self.imputer.transform(Xf)
        X_scaled = self.scaler.transform(X_imp)
        return X_scaled

    def fit_transform(self, X: pd.DataFrame, y=None) -> np.ndarray:
        """Convenience: fit then transform in one call."""
        self.fit(X, y)
        return self.transform(X)

    # ─────────────────────────────────────────────────────────────────────────
    def validate_data(self, df: pd.DataFrame) -> dict:
        """
        Run data quality checks and return a structured quality report.

        Returns
        -------
        dict with keys:
            n_samples, n_features, missing_values, missing_pct,
            duplicates, outliers_per_feature, overall_outlier_pct,
            quality_score (0-100)
        """
        report = {
            'n_samples':           len(df),
            'n_features':          len(self.feature_columns),
            'missing_values':      {},
            'missing_pct':         {},
            'duplicates':          int(df.duplicated().sum()),
            'outliers_per_feature': {},
            'overall_outlier_pct': 0.0,
            'quality_score':       100.0,
            'warnings':            [],
        }

        total_outliers = 0
        total_cells    = 0

        for col in self.feature_columns:
            if col not in df.columns:
                report['missing_values'][col]  = len(df)
                report['missing_pct'][col]     = 100.0
                report['warnings'].append(f"Column '{col}' entirely absent.")
                continue

            n_missing = int(df[col].isna().sum())
            report['missing_values'][col] = n_missing
            report['missing_pct'][col]    = round(n_missing / len(df) * 100, 2)

            if col in VALID_RANGES:
                lo, hi = VALID_RANGES[col]
                n_out = int(((df[col] < lo) | (df[col] > hi)).sum())
                report['outliers_per_feature'][col] = n_out
                total_outliers += n_out

            total_cells += len(df)

        report['overall_outlier_pct'] = round(total_outliers / max(total_cells, 1) * 100, 2)

        # Quality score deductions
        total_missing_pct = np.mean(list(report['missing_pct'].values()))
        score = 100.0
        score -= min(total_missing_pct * 2, 30)             # up to -30 for missing
        score -= min(report['overall_outlier_pct'] * 3, 20) # up to -20 for outliers
        score -= min(report['duplicates'] / len(df) * 100, 10)  # up to -10 for dupes
        report['quality_score'] = round(max(score, 0.0), 1)

        if report['duplicates'] > 0:
            report['warnings'].append(f"{report['duplicates']} duplicate rows found.")
        if report['overall_outlier_pct'] > 5:
            report['warnings'].append(f"High outlier rate: {report['overall_outlier_pct']:.1f}%.")

        return report

    # ─────────────────────────────────────────────────────────────────────────
    def save(self, path: str):
        """Persist fitted preprocessor (imputer + scaler) to disk."""
        if not self._fitted:
            raise RuntimeError("Cannot save an unfitted preprocessor.")
        obj = {
            'imputer':         self.imputer,
            'scaler':          self.scaler,
            'feature_columns': self.feature_columns,
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(obj, path)
        logger.info(f"Preprocessor saved → {path}")

    def load(self, path: str) -> 'LandslidePreprocessor':
        """Load a previously saved preprocessor."""
        obj = joblib.load(path)
        self.imputer         = obj['imputer']
        self.scaler          = obj['scaler']
        self.feature_columns = obj['feature_columns']
        self._fitted          = True
        logger.info(f"Preprocessor loaded ← {path}")
        return self

    # ─────────────────────────────────────────────────────────────────────────
    def _select_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Select and order feature columns, adding zeros for missing ones."""
        missing = [c for c in self.feature_columns if c not in X.columns]
        if missing:
            logger.warning(f"Missing columns (filled with NaN): {missing}")
            for col in missing:
                X = X.copy()
                X[col] = np.nan
        return X[self.feature_columns].copy()

    def _clip_extremes(self, X: pd.DataFrame) -> pd.DataFrame:
        """Clip values to domain-realistic extremes before scaling."""
        X = X.copy()
        for col in X.columns:
            if col in VALID_RANGES:
                lo, hi = VALID_RANGES[col]
                X[col] = X[col].clip(lo, hi)
        return X
