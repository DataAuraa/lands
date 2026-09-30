"""
Database configuration and session management.
Supports PostgreSQL/PostGIS in production/Docker,
and gracefully falls back to SQLite for local development/testing without PostGIS.
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

database_url = settings.DATABASE_URL

# Fallback to local SQLite if postgres is unreachable in direct dev mode without docker
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, connect_args=connect_args)
else:
    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20
        )
    except Exception as e:
        logger.warning(f"Failed to initialize engine with {database_url}: {e}. Falling back to SQLite.")
        database_url = "sqlite:///./landslide_dev.db"
        engine = create_engine(database_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables and PostGIS extension if applicable."""
    # Attempt PostGIS extension creation on PostgreSQL
    if "postgresql" in str(engine.url):
        try:
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
                conn.commit()
                logger.info("PostGIS extension ensured.")
        except Exception as e:
            logger.warning(f"Could not enable PostGIS extension (may already exist or insufficient permissions): {e}")

    # Import all models so Base.metadata is fully populated
    import app.models  # noqa
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
