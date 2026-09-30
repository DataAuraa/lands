"""
Satellite imagery and remote sensing indicators database model.
Supports optical/SAR imagery indicators (NDVI, NDMI, surface change).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SatelliteData(Base):
    __tablename__ = "satellite_data"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    acquisition_time = Column(DateTime, default=datetime.utcnow, index=True)
    satellite_name = Column(String(50), default="Sentinel-2")
    image_url = Column(String(500), nullable=True)
    cloud_percentage = Column(Float, default=10.0)
    
    # Remote sensing spectral indices
    ndvi = Column(Float, default=0.6)           # Normalized Difference Vegetation Index (-1 to +1)
    ndmi = Column(Float, default=0.4)           # Normalized Difference Moisture Index (-1 to +1)
    change_score = Column(Float, default=0.0)   # Surface deformation / landslide scar change score (0 to 1)
    
    source = Column(String(50), default="DEMO")  # 'SENTINEL', 'LANDSAT', 'DEMO'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="satellite_records")
