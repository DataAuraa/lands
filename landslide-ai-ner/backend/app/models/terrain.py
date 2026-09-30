"""
DEM-derived terrain features database model.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class TerrainData(Base):
    __tablename__ = "terrain_data"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # DEM derivatives
    elevation = Column(Float, nullable=False)          # meters above sea level
    slope = Column(Float, nullable=False)              # degrees (0 - 90)
    aspect = Column(Float, default=0.0)                # degrees (0 - 360)
    curvature = Column(Float, default=0.0)             # profile curvature
    drainage_density = Column(Float, default=0.0)      # km/km²
    terrain_ruggedness = Column(Float, default=0.0)    # TRI index
    
    # Environmental context
    land_cover = Column(String(100), default="mixed_forest")
    geology = Column(String(100), default="sedimentary")
    distance_to_road = Column(Float, default=0.5)      # km
    distance_to_river = Column(Float, default=1.0)     # km
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="terrain_info")
