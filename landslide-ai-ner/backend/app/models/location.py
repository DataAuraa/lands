"""
Location database model representing monitored landslide zones in NER.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base

try:
    from geoalchemy2 import Geometry
    HAS_GEOALCHEMY = True
except ImportError:
    HAS_GEOALCHEMY = False


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    block = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, default=0.0)  # meters
    population = Column(Integer, default=0)
    road_connectivity = Column(String(50), default="paved")  # paved, unpaved, cut-off, highway
    infrastructure_type = Column(String(100), default="residential")  # residential, railway, highway, school, hospital
    
    # Terrain parameters (denormalized for rapid query)
    slope = Column(Float, default=0.0)  # degrees
    aspect = Column(Float, default=0.0)  # degrees
    curvature = Column(Float, default=0.0)
    drainage_density = Column(Float, default=0.0)
    land_cover = Column(String(100), default="mixed_forest")
    geology = Column(String(100), default="sedimentary")
    distance_to_road = Column(Float, default=1.0)  # km
    distance_to_river = Column(Float, default=1.0)  # km
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # PostGIS geometry column (if GeoAlchemy2 is installed)
    if HAS_GEOALCHEMY:
        geom = Column(Geometry('POINT', srid=4326), nullable=True)

    # Relationships
    sensors = relationship("SoilSensor", back_populates="location", cascade="all, delete-orphan")
    terrain_info = relationship("TerrainData", back_populates="location", uselist=False, cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="location", order_by="desc(Prediction.timestamp)")
    alerts = relationship("Alert", back_populates="location", order_by="desc(Alert.created_at)")
    field_reports = relationship("FieldReport", back_populates="location")
    satellite_records = relationship("SatelliteData", back_populates="location")
    historical_events = relationship("HistoricalLandslide", back_populates="location")
