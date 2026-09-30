"""
Feature engineering for the NER Landslide Risk ML pipeline.
Adds derived geophysical and hydrometeorological features.
"""
import numpy as np
import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# ── Land-cover risk coefficients (domain-calibrated) ──────────────────────────
LAND_COVER_RISK = {
    0: 0.15,   # dense_forest   – roots bind soil
    1: 0.25,   # mixed_forest
    2: 0.45,   # shrubland      – less root depth
    3: 0.50,   # agricultural   – disturbed soil, irrigation wetting
    4: 0.75,   # bare_soil      – highest erosion risk
    5: 0.60,   # urban          – impervious surface → high runoff
    6: 0.35,   # grassland
}

# Feature descriptions for explainability
ENGINEERED_FEATURE_DESCRIPTIONS = {
    'rainfall_intensity_ratio':   'Ratio of short-term to 24-hour rainfall intensity',
    'soil_saturation':            'Fractional soil saturation (0–1)',
    'slope_radians':              'Terrain slope in radians',
    'slope_tan':                  'Tangent of slope (shear stress proxy)',
    'terrain_instability':        'Slope × saturation interaction (instability index)',
    'combined_rainfall':          'Weighted antecedent rainfall accumulation',
    'antecedent_moisture_index':  'Weighted sum of antecedent rainfall (AMI)',
    'land_cover_risk':            'Land-cover-derived slope erosion risk coefficient',
    'rainfall_slope_interaction': 'Rainfall × slope interaction term',
    'drainage_efficiency':        'Slope-adjusted drainage efficiency index',
    'vegetation_stability':       'NDVI-based vegetation stability factor',
    'river_proximity_factor':     'Proximity to river (flood susceptibility proxy)',
}


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived geophysical and hydrometeorological features to the dataset.

    All features are domain-motivated by NER geology and hydrology:
    - Steep slopes + saturated soils are the leading trigger in Manipur / Nagaland
    - Antecedent rainfall (AMI) is critical for failure triggering
    - NDVI loss correlates strongly with recent landslide scars

    Parameters
    ----------
    df : pd.DataFrame
        Raw feature dataframe. Must contain base FEATURE_COLUMNS.

    Returns
    -------
    pd.DataFrame with additional engineered features appended.
    """
    df = df.copy()

    # ── Rainfall-derived features ──────────────────────────────────────────────
    if 'rainfall_24h' in df.columns:
        r24  = df['rainfall_24h'].clip(lower=0)
        r72  = df.get('rainfall_72h', pd.Series(np.zeros(len(df)), index=df.index)).clip(lower=0)
        r12  = df.get('rainfall_12h', r24 * 0.4).clip(lower=0)   # estimate if absent
        r6   = df.get('rainfall_6h',  r24 * 0.15).clip(lower=0)
        r1   = df.get('rainfall_1h',  r24 * 0.04).clip(lower=0)

        # Intensity ratio: how much of the 24h rain fell in the last hour
        df['rainfall_intensity_ratio'] = (r1 / (r24 + 1.0)).round(4)

        # Weighted antecedent rainfall (AMI) – exponential decay weighting
        # Weights: 24h window most important, then 72h residual
        df['combined_rainfall'] = (
            0.40 * r24 +
            0.30 * r72 +
            0.20 * r12 +
            0.10 * r6
        ).round(3)

        # Antecedent Moisture Index (API-like):
        # AMI = sum(Ri / k^i) where k=0.9 decay factor, i=day index
        # Approximate with available rainfall windows
        df['antecedent_moisture_index'] = (
            r24 * 1.00 +
            (r72 - r24).clip(lower=0) * 0.81 +   # day -2 + -3 contribution
            r6  * 0.59                             # short burst contribution
        ).round(3)

    # ── Terrain-derived features ───────────────────────────────────────────────
    if 'slope' in df.columns:
        slope_rad              = df['slope'] * np.pi / 180.0
        df['slope_radians']    = slope_rad.round(5)
        df['slope_tan']        = np.tan(slope_rad).round(5)   # shear stress proxy

    # ── Soil saturation ────────────────────────────────────────────────────────
    if 'soil_moisture' in df.columns:
        df['soil_saturation'] = (df['soil_moisture'] / 100.0).round(4)

    # ── Terrain instability index ──────────────────────────────────────────────
    # Physics: Factor of Safety ∝ cohesion / (tan(slope) × density × g × depth)
    # Instability proxy: slope_tan × soil_saturation captures this relationship
    if 'slope_tan' in df.columns and 'soil_saturation' in df.columns:
        df['terrain_instability'] = (df['slope_tan'] * df['soil_saturation']).round(5)

    # ── Rainfall × slope interaction ───────────────────────────────────────────
    if 'rainfall_24h' in df.columns and 'slope' in df.columns:
        df['rainfall_slope_interaction'] = (
            (df['rainfall_24h'] / 400.0) * (df['slope'] / 65.0)
        ).round(4)

    # ── Land cover risk coefficient ────────────────────────────────────────────
    if 'land_cover_encoded' in df.columns:
        df['land_cover_risk'] = df['land_cover_encoded'].map(LAND_COVER_RISK).fillna(0.35)

    # ── Drainage efficiency ────────────────────────────────────────────────────
    if 'drainage_density' in df.columns and 'slope' in df.columns:
        # High drainage density on steep slopes → rapid runoff → high risk
        df['drainage_efficiency'] = (
            df['drainage_density'] / 8.0 * df['slope'] / 65.0
        ).round(4)

    # ── Vegetation stability ───────────────────────────────────────────────────
    if 'ndvi' in df.columns:
        # NDVI ∈ [-0.1, 0.9]; normalize so high NDVI = high stability
        df['vegetation_stability'] = ((df['ndvi'] + 0.1) / 1.0).clip(0, 1).round(4)

    # ── River proximity factor ─────────────────────────────────────────────────
    if 'distance_to_river' in df.columns:
        # Inverse log proximity – closer to river = higher base saturation
        df['river_proximity_factor'] = (
            1.0 / np.log1p(df['distance_to_river'])
        ).round(4)

    n_new = len([c for c in df.columns
                 if c in ENGINEERED_FEATURE_DESCRIPTIONS])
    logger.debug(f"Engineered {n_new} derived features; total columns: {len(df.columns)}")
    return df


def create_feature_matrix(raw_features: dict) -> pd.DataFrame:
    """
    Convert raw API input (single location dict) into a feature DataFrame
    suitable for the ML model.

    Parameters
    ----------
    raw_features : dict
        Keys should match FEATURE_COLUMNS from data_loader.py. Missing
        numeric keys are filled with domain-sensible defaults.

    Returns
    -------
    pd.DataFrame with one row (after engineer_features applied).
    """
    DEFAULTS = {
        'slope':                     25.0,
        'elevation':                 800.0,
        'aspect':                    180.0,
        'curvature':                 0.0,
        'drainage_density':          3.0,
        'rainfall_24h':              10.0,
        'rainfall_72h':              25.0,
        'rainfall_12h':              5.0,
        'rainfall_6h':               2.0,
        'rainfall_1h':               0.5,
        'soil_moisture':             40.0,
        'land_cover_encoded':        1,
        'distance_to_road':          2.0,
        'distance_to_river':         5.0,
        'previous_landslide':        0,
        'historical_susceptibility': 0.3,
        'ndvi':                      0.6,
        'change_score':              0.1,
    }

    row = {**DEFAULTS, **raw_features}   # overlay provided values on defaults
    df  = pd.DataFrame([row])
    df  = engineer_features(df)
    return df


def get_all_feature_names(base_only: bool = False) -> list:
    """Return list of all feature names (base + engineered)."""
    base = [
        'slope', 'elevation', 'aspect', 'curvature', 'drainage_density',
        'rainfall_24h', 'rainfall_72h', 'soil_moisture', 'land_cover_encoded',
        'distance_to_road', 'distance_to_river', 'previous_landslide',
        'historical_susceptibility', 'ndvi', 'change_score'
    ]
    if base_only:
        return base
    engineered = list(ENGINEERED_FEATURE_DESCRIPTIONS.keys())
    return base + engineered
