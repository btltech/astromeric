import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./astronumerology.db")

# Support SQLite (dev) and Postgres (production) via DATABASE_URL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
    )
else:
    # Production PostgreSQL with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before use
        echo=False
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_paid = Column(Boolean, default=False)  # Premium subscription status
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Notification preferences
    alert_mercury_retrograde = Column(Boolean, default=True)  # Receive retrograde alerts
    alert_frequency = Column(String(20), default="every_retrograde")  # "every_retrograde", "once_per_year", "weekly_digest", "none"
    last_retrograde_alert = Column(DateTime, nullable=True)  # Timestamp of last alert sent

    # Relationship to profiles
    profiles = relationship("Profile", back_populates="owner")


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Add length limit
    date_of_birth = Column(String, nullable=False)  # ISO format
    time_of_birth = Column(String, nullable=True)
    place_of_birth = Column(String(255), nullable=True)  # Add length limit
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String(50), default="UTC")  # Add length limit
    house_system = Column(String(20), default="Placidus")  # Add length limit
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # User ownership (optional for guest users)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="profiles")
    readings = relationship("Reading", back_populates="profile")
    favourites = relationship("Favourite", back_populates="profile")
    preferences = relationship("Preference", back_populates="profile")

    # Database indexes for performance
    __table_args__ = (
        Index('idx_profile_user_created', 'user_id', 'created_at'),
        Index('idx_profile_date_of_birth', 'date_of_birth'),
        Index('idx_profile_name', 'name'),
    )


class Reading(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    scope = Column(String(20), nullable=False)  # daily, weekly, monthly
    date = Column(String, nullable=False)  # ISO date for the reading
    content = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    feedback = Column(String(20), nullable=True)  # yes/no/neutral
    journal = Column(Text, nullable=True)

    profile = relationship("Profile", back_populates="readings")
    favourites = relationship("Favourite", back_populates="reading")

    # Database indexes for performance
    __table_args__ = (
        Index('idx_reading_profile_scope_date', 'profile_id', 'scope', 'date'),
        Index('idx_reading_created_at', 'created_at'),
    )


class Favourite(Base):
    __tablename__ = "favourites"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    reading_id = Column(Integer, ForeignKey("readings.id"), nullable=False)

    profile = relationship("Profile", back_populates="favourites")
    reading = relationship("Reading", back_populates="favourites")


class Preference(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    focus = Column(String, default="general")  # love, career, spiritual, general
    tone = Column(String, default="balanced")  # softer, direct, balanced

    profile = relationship("Profile", back_populates="preferences")


class SectionFeedback(Base):
    __tablename__ = "section_feedback"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=True)
    scope = Column(String, nullable=False)
    section = Column(String, nullable=False)
    vote = Column(String, nullable=False)  # "up" or "down"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Create tables
Base.metadata.create_all(bind=engine)
