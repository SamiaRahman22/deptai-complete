"""User database model."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    student = "student"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    student_id = Column(String(50), unique=True, nullable=True)  # null for admins
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="student", nullable=False)
    department = Column(String(100), default="Computer Science & Engineering")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    query_logs = relationship("QueryLog", back_populates="user", lazy="dynamic")
