from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    progress = relationship("FamilyProgress", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("WorkoutSession", back_populates="user", cascade="all, delete-orphan")


class FamilyProgress(Base):
    __tablename__ = "family_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    family = Column(String, nullable=False)
    exercise_index = Column(Integer, nullable=False, default=0)

    __table_args__ = (UniqueConstraint("user_id", "family", name="uq_user_family"),)

    user = relationship("User", back_populates="progress")


class WorkoutSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    family = Column(String, nullable=False, index=True)
    exercise_name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    sets = Column(Text, nullable=False)  # JSON-encoded list[int]
    form_good = Column(Boolean, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="sessions")


Index("ix_sessions_user_family_date", WorkoutSession.user_id, WorkoutSession.family, WorkoutSession.date)
