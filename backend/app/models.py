import os
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
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
    engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to profiles
    profiles = relationship("Profile", back_populates="owner")


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date_of_birth = Column(String, nullable=False)  # ISO format
    time_of_birth = Column(String, nullable=True)
    place_of_birth = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String, default="UTC")
    house_system = Column(String, default="Placidus")
    created_at = Column(DateTime, default=datetime.utcnow)
    # User ownership (optional for guest users)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="profiles")
    readings = relationship("Reading", back_populates="profile")
    favourites = relationship("Favourite", back_populates="profile")
    preferences = relationship("Preference", back_populates="profile")


class Reading(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    scope = Column(String, nullable=False)  # daily, weekly, monthly
    date = Column(String, nullable=False)  # ISO date for the reading
    content = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    feedback = Column(String, nullable=True)  # yes/no/neutral
    journal = Column(Text, nullable=True)

    profile = relationship("Profile", back_populates="readings")
    favourites = relationship("Favourite", back_populates="reading")


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


# Create tables
Base.metadata.create_all(bind=engine)
