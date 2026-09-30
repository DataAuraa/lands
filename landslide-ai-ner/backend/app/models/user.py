"""
User database model with role-based access.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    # Roles: admin, district_admin, dma, field_officer, citizen
    role = Column(String(30), nullable=False, default="citizen")
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    preferred_language = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    field_reports = relationship("FieldReport", back_populates="reporter", foreign_keys="FieldReport.user_id")
    verified_reports = relationship("FieldReport", back_populates="verifier", foreign_keys="FieldReport.verified_by")
    audit_logs = relationship("AuditLog", back_populates="user")
