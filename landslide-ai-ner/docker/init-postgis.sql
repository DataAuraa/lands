-- ============================================================
-- PostGIS Initialization Script
-- AI-Based Early Warning & Landslide Risk Monitoring System
-- NER (North-East Region)
-- ============================================================

-- Enable PostGIS spatial extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_raster;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable additional indexing support
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable case-insensitive text
CREATE EXTENSION IF NOT EXISTS citext;

-- Enable cryptographic functions (for password hashing fallback)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ── Create application schema ─────────────────────────────
CREATE SCHEMA IF NOT EXISTS landslide;

-- ── Set search path ───────────────────────────────────────
ALTER DATABASE landslide_ner SET search_path TO landslide, public;

-- ── Verify spatial reference system for WGS84 ────────────
-- SRID 4326 = WGS84 (GPS coordinates)
-- Should already exist in PostGIS, but verify:
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM spatial_ref_sys WHERE srid = 4326) THEN
    RAISE EXCEPTION 'SRID 4326 (WGS84) not found — PostGIS installation may be incomplete';
  END IF;
  RAISE NOTICE 'PostGIS initialized successfully. Version: %', PostGIS_Version();
END $$;

-- ── Create enum types ─────────────────────────────────────
DO $$
BEGIN

  -- Alert severity levels
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'alert_severity') THEN
    CREATE TYPE alert_severity AS ENUM ('LOW', 'MODERATE', 'HIGH', 'CRITICAL', 'EXTREME');
  END IF;

  -- Risk levels for monitoring locations
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'risk_level') THEN
    CREATE TYPE risk_level AS ENUM ('VERY_LOW', 'LOW', 'MODERATE', 'HIGH', 'VERY_HIGH', 'CRITICAL');
  END IF;

  -- User roles
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
    CREATE TYPE user_role AS ENUM ('ADMIN', 'DISTRICT_ADMIN', 'FIELD_OFFICER', 'CITIZEN', 'VIEWER');
  END IF;

  -- Alert status
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'alert_status') THEN
    CREATE TYPE alert_status AS ENUM ('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED', 'EXPIRED', 'FALSE_ALARM');
  END IF;

  -- Sensor types
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sensor_type') THEN
    CREATE TYPE sensor_type AS ENUM (
      'RAINFALL_GAUGE', 'SOIL_MOISTURE', 'ACCELEROMETER',
      'INCLINOMETER', 'PIEZOMETER', 'WATER_LEVEL',
      'EXTENSOMETER', 'WEATHER_STATION', 'SIMULATED'
    );
  END IF;

  -- NER States covered by the system
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ner_state') THEN
    CREATE TYPE ner_state AS ENUM (
      'ASSAM', 'MEGHALAYA', 'MANIPUR', 'MIZORAM',
      'NAGALAND', 'TRIPURA', 'ARUNACHAL_PRADESH', 'SIKKIM'
    );
  END IF;

END $$;

-- ── Log initialization ────────────────────────────────────
DO $$
BEGIN
  RAISE NOTICE '=======================================================';
  RAISE NOTICE 'Landslide NER Database Initialized';
  RAISE NOTICE 'PostGIS Version : %', PostGIS_Lib_Version();
  RAISE NOTICE 'PostgreSQL      : %', current_setting('server_version');
  RAISE NOTICE 'Database        : %', current_database();
  RAISE NOTICE 'Timestamp       : %', NOW();
  RAISE NOTICE 'SIMULATION MODE : TRUE (Development/Demo)';
  RAISE NOTICE '=======================================================';
END $$;
