"""
Data loader for landslide ML pipeline.
Loads from PostgreSQL DB or CSV files.
All synthetic data is statistically realistic for Northeast India (NER).
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LandslideDataLoader:
    """
    Loads landslide training data from CSV, PostgreSQL, or generates
    a statistically realistic synthetic NER dataset.
    """

    FEATURE_COLUMNS = [
        'slope', 'elevation', 'aspect', 'curvature', 'drainage_density',
        'rainfall_24h', 'rainfall_72h', 'soil_moisture', 'land_cover_encoded',
        'distance_to_road', 'distance_to_river', 'previous_landslide',
        'historical_susceptibility', 'ndvi', 'change_score'
    ]
    TARGET_COLUMN = 'landslide_occurred'

    # NER-specific realistic ranges
    NER_RANGES = {
        'slope':                  (5.0,   65.0),
        'elevation':              (100.0, 3500.0),
        'aspect':                 (0.0,   360.0),
        'curvature':              (-5.0,  5.0),
        'drainage_density':       (0.5,   8.0),
        'rainfall_24h':           (0.0,   400.0),   # Cherrapunji can exceed 300mm/day
        'rainfall_72h':           (0.0,   900.0),
        'soil_moisture':          (10.0,  95.0),
        'distance_to_road':       (0.1,   15.0),    # km
        'distance_to_river':      (0.1,   20.0),    # km
        'ndvi':                   (-0.1,  0.9),
        'change_score':           (0.0,   1.0),
        'historical_susceptibility': (0.0, 1.0),
    }

    LAND_COVER_TYPES = {
        'dense_forest':    0,
        'mixed_forest':    1,
        'shrubland':       2,
        'agricultural':    3,
        'bare_soil':       4,
        'urban':           5,
        'grassland':       6,
    }

    def load_from_csv(self, path: str) -> pd.DataFrame:
        """Load dataset from a CSV file and validate required columns."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        df = pd.read_csv(p)
        logger.info(f"Loaded {len(df)} records from {path}")

        missing_features = [c for c in self.FEATURE_COLUMNS if c not in df.columns]
        if missing_features:
            logger.warning(f"Missing feature columns: {missing_features}")

        if self.TARGET_COLUMN not in df.columns:
            logger.warning(f"Target column '{self.TARGET_COLUMN}' not found in CSV.")

        return df

    def load_from_db(self, db_url: str) -> pd.DataFrame:
        """
        Join weather, terrain, satellite, and historical tables from PostgreSQL.
        Requires SQLAlchemy and psycopg2.
        """
        try:
            from sqlalchemy import create_engine, text
        except ImportError:
            raise ImportError("Install sqlalchemy and psycopg2: pip install sqlalchemy psycopg2")

        engine = create_engine(db_url)
        query = text("""
            SELECT
                t.id,
                t.latitude,
                t.longitude,
                t.slope,
                t.elevation,
                t.aspect,
                t.curvature,
                t.drainage_density,
                t.distance_to_road,
                t.distance_to_river,
                t.land_cover,
                t.historical_susceptibility,
                w.rainfall_24h,
                w.rainfall_72h,
                w.soil_moisture,
                s.ndvi,
                s.change_score,
                h.previous_landslide,
                h.landslide_occurred
            FROM terrain t
            LEFT JOIN weather_observations w
                ON t.id = w.location_id AND w.observation_date = CURRENT_DATE - INTERVAL '1 day'
            LEFT JOIN satellite_data s
                ON t.id = s.location_id AND s.acquisition_date >= CURRENT_DATE - INTERVAL '30 days'
            LEFT JOIN historical_events h
                ON t.id = h.location_id
            WHERE w.observation_date IS NOT NULL
        """)

        with engine.connect() as conn:
            df = pd.read_sql(query, conn)

        # Encode land cover
        df['land_cover_encoded'] = df['land_cover'].map(self.LAND_COVER_TYPES).fillna(1)
        df.drop(columns=['land_cover'], inplace=True, errors='ignore')
        logger.info(f"Loaded {len(df)} records from database.")
        return df

    def generate_synthetic_dataset(self, n_samples: int = 2000, seed: int = 42) -> pd.DataFrame:
        """
        Generate a statistically realistic NER landslide dataset.

        Domain knowledge applied:
        - NER receives among the highest rainfall globally (Cherrapunji, Meghalaya)
        - Slopes of 30–65° are common in Manipur, Nagaland, Mizoram hill ranges
        - Class imbalance: ~15% landslide events (realistic for high-susceptibility zones)
        - Landslide probability driven by:
            * rainfall_24h (strongest trigger)
            * soil_moisture (antecedent condition)
            * slope (terrain factor)
            * historical_susceptibility (spatial factor)
            * change_score (recent instability)
        """
        rng = np.random.default_rng(seed)
        n = n_samples

        # ── Terrain features (relatively static, correlated) ──────────────────
        slope = rng.beta(2.5, 2.0) * 60 + 5               # 5–65°, peak ~35°
        slope = rng.beta(2.5, 2.0, n) * 60 + 5

        # Elevation correlated with slope in NER hill ranges
        elevation_base = slope * 40 + rng.normal(800, 300, n)
        elevation = np.clip(elevation_base, 100, 3500)

        aspect = rng.uniform(0, 360, n)                    # degrees

        # Curvature: mostly concave/convex, small values
        curvature = rng.normal(0, 1.5, n)
        curvature = np.clip(curvature, -5, 5)

        # Drainage density higher in steeper terrain
        drainage_density = 0.8 + slope / 15.0 + rng.normal(0, 0.5, n)
        drainage_density = np.clip(drainage_density, 0.5, 8.0)

        # Distance to road: shorter near valleys
        distance_to_road = rng.exponential(3.0, n)
        distance_to_road = np.clip(distance_to_road, 0.1, 15.0)

        distance_to_river = rng.exponential(5.0, n)
        distance_to_river = np.clip(distance_to_river, 0.1, 20.0)

        # Historical susceptibility: correlated with slope & drainage
        hist_susc_raw = (slope / 65.0) * 0.5 + (drainage_density / 8.0) * 0.3 + rng.beta(2, 5, n) * 0.2
        historical_susceptibility = np.clip(hist_susc_raw, 0.0, 1.0)

        # Previous landslide (binary): more likely where susceptibility is high
        previous_landslide = (rng.random(n) < (0.1 + historical_susceptibility * 0.4)).astype(int)

        # ── Land cover ─────────────────────────────────────────────────────────
        # NER: ~65% forest, 15% agricultural, 10% shrub, 5% bare, 5% other
        lc_probs = [0.35, 0.30, 0.15, 0.12, 0.04, 0.02, 0.02]
        land_cover_encoded = rng.choice(len(lc_probs), n, p=lc_probs)

        # NDVI: higher for dense forest, lower for bare/urban
        ndvi_base = {0: 0.75, 1: 0.65, 2: 0.45, 3: 0.35, 4: 0.10, 5: 0.15, 6: 0.55}
        ndvi = np.array([ndvi_base[lc] for lc in land_cover_encoded])
        ndvi += rng.normal(0, 0.05, n)
        ndvi = np.clip(ndvi, -0.1, 0.9)

        # ── Rainfall (seasonal, autocorrelated) ────────────────────────────────
        # NER monsoon (Jun–Sep): very heavy rainfall
        # Simulate "season" for each sample (monsoon vs dry)
        is_monsoon = rng.random(n) < 0.55   # 55% of samples from monsoon period

        # Rainfall 24h: monsoon follows gamma distribution, dry is near zero
        rainfall_24h_monsoon = rng.gamma(2.5, 18.0, n)     # mean ~45mm, can reach 400+
        rainfall_24h_dry     = rng.gamma(1.2, 2.5, n)       # mean ~3mm
        rainfall_24h = np.where(is_monsoon, rainfall_24h_monsoon, rainfall_24h_dry)

        # Add extreme events (Cherrapunji-level): ~8% of monsoon days
        extreme_mask = is_monsoon & (rng.random(n) < 0.08)
        rainfall_24h[extreme_mask] += rng.gamma(3, 50, extreme_mask.sum())  # +150–300mm
        rainfall_24h = np.clip(rainfall_24h, 0, 400)

        # Rainfall 72h: 3-day accumulation (autocorrelated with 24h)
        rainfall_72h = rainfall_24h * rng.uniform(2.2, 3.5, n) + rng.gamma(1.5, 5.0, n)
        rainfall_72h = np.where(is_monsoon, rainfall_72h, rainfall_72h * 0.4)
        rainfall_72h = np.clip(rainfall_72h, 0, 900)

        # ── Soil moisture ───────────────────────────────────────────────────────
        # Responds to rainfall and season; higher near rivers
        moisture_base = 30 + (rainfall_24h / 400) * 50 + (rainfall_72h / 900) * 20
        moisture_base += rng.normal(0, 8, n)
        moisture_base -= distance_to_river * 0.5   # dries away from rivers
        soil_moisture = np.clip(moisture_base, 10, 95)

        # ── Satellite change score ──────────────────────────────────────────────
        # Higher after recent disturbances / heavy rain
        change_score_raw = (rainfall_24h / 400) * 0.4 + rng.beta(1.5, 5, n) * 0.6
        change_score = np.clip(change_score_raw, 0, 1)

        # ── Compute landslide probability (physics-informed) ────────────────────
        slope_norm    = slope / 65.0
        rain_norm     = rainfall_24h / 400.0
        moist_norm    = soil_moisture / 95.0
        hist_norm     = historical_susceptibility
        change_norm   = change_score

        # Logistic-like score
        log_odds = (
            -3.5
            + 4.2 * rain_norm
            + 3.0 * slope_norm
            + 2.5 * moist_norm
            + 1.8 * hist_norm
            + 1.5 * change_norm
            + 1.2 * (rain_norm * moist_norm)    # interaction: wet soil + heavy rain
            + 0.8 * previous_landslide
            - 0.5 * (ndvi * 2)                  # vegetation stabilises slope
        )
        prob_landslide = 1 / (1 + np.exp(-log_odds))
        prob_landslide = np.clip(prob_landslide, 0.01, 0.99)

        # Sample binary labels; calibrate to ~15% positive rate
        raw_labels = (rng.random(n) < prob_landslide).astype(int)
        current_rate = raw_labels.mean()
        target_rate  = 0.15

        # Adjust threshold if needed
        if current_rate > target_rate + 0.05:
            sorted_probs = np.sort(prob_landslide)[::-1]
            threshold = sorted_probs[int(n * target_rate)]
            landslide_occurred = (prob_landslide >= threshold).astype(int)
        elif current_rate < target_rate - 0.05:
            boost = target_rate / current_rate
            landslide_occurred = (rng.random(n) < np.clip(prob_landslide * boost, 0, 1)).astype(int)
        else:
            landslide_occurred = raw_labels

        # ── Assemble DataFrame ─────────────────────────────────────────────────
        df = pd.DataFrame({
            'slope':                  slope.round(2),
            'elevation':              elevation.round(1),
            'aspect':                 aspect.round(1),
            'curvature':              curvature.round(3),
            'drainage_density':       drainage_density.round(3),
            'rainfall_24h':           rainfall_24h.round(2),
            'rainfall_72h':           rainfall_72h.round(2),
            'soil_moisture':          soil_moisture.round(2),
            'land_cover_encoded':     land_cover_encoded,
            'distance_to_road':       distance_to_road.round(3),
            'distance_to_river':      distance_to_river.round(3),
            'previous_landslide':     previous_landslide,
            'historical_susceptibility': historical_susceptibility.round(4),
            'ndvi':                   ndvi.round(4),
            'change_score':           change_score.round(4),
            'landslide_occurred':     landslide_occurred,
            # Meta columns (not used as features)
            'is_monsoon':             is_monsoon.astype(int),
            'prob_score':             prob_landslide.round(4),
        })

        pos_rate = df['landslide_occurred'].mean()
        logger.info(
            f"Synthetic dataset: {n} samples | "
            f"Positive rate: {pos_rate:.1%} | "
            f"Monsoon fraction: {is_monsoon.mean():.1%}"
        )
        return df

    def get_feature_columns(self) -> list:
        return self.FEATURE_COLUMNS

    def get_target_column(self) -> str:
        return self.TARGET_COLUMN
