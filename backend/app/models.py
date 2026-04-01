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
    text,
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
        echo=False,
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for Apple users
    is_active = Column(Boolean, default=True)
    is_paid = Column(Boolean, default=False)  # Premium subscription status
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Apple Sign-In / OAuth fields
    external_id = Column(String, unique=True, index=True, nullable=True)  # Apple user ID
    auth_provider = Column(String(20), nullable=True)  # "apple", "google", etc.
    full_name = Column(String(255), nullable=True)  # From Apple Sign-In

    # Notification preferences
    alert_mercury_retrograde = Column(
        Boolean, default=True
    )  # Receive retrograde alerts
    alert_frequency = Column(
        String(20), default="every_retrograde"
    )  # "every_retrograde", "once_per_year", "weekly_digest", "none"
    last_retrograde_alert = Column(
        DateTime, nullable=True
    )  # Timestamp of last alert sent

    # Relationship to profiles
    profiles = relationship("Profile", back_populates="owner")


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Add length limit
    date_of_birth = Column(String, nullable=False)  # ISO format
    time_of_birth = Column(String, nullable=True)
    time_confidence = Column(String(20), nullable=True, default="unknown")  # exact / approximate / unknown
    place_of_birth = Column(String(255), nullable=True)  # Add length limit
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String(50), default="UTC")  # Add length limit
    house_system = Column(String(20), default="Placidus")  # Add length limit
    data_quality = Column(String(20), nullable=True)  # full / date_and_place / date_only (computed on save)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # User ownership (optional for guest users)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="profiles")
    readings = relationship("Reading", back_populates="profile")
    favourites = relationship("Favourite", back_populates="profile")
    preferences = relationship("Preference", back_populates="profile")

    # Database indexes for performance
    __table_args__ = (
        Index("idx_profile_user_created", "user_id", "created_at"),
        Index("idx_profile_date_of_birth", "date_of_birth"),
        Index("idx_profile_name", "name"),
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
        Index("idx_reading_profile_scope_date", "profile_id", "scope", "date"),
        Index("idx_reading_created_at", "created_at"),
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


class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    platform = Column(String(20), default="ios")
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TransitSubscription(Base):
    __tablename__ = "transit_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# Create tables
Base.metadata.create_all(bind=engine)


def _ensure_sqlite_schema() -> None:
    """
    Lightweight SQLite schema migration.

    This repo historically shipped a tracked sqlite DB for local/dev usage.
    `create_all()` does not add missing columns to existing tables, so older DBs
    can break newer code paths. For SQLite only, patch up missing columns at
    runtime to keep local dev/test usable.
    """

    if not DATABASE_URL.startswith("sqlite"):
        return

    with engine.begin() as conn:
        def existing_columns(table: str) -> set[str]:
            rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
            return {r[1] for r in rows}  # (cid, name, type, notnull, dflt_value, pk)

        def add_column_if_missing(table: str, name: str, definition_sql: str) -> None:
            cols = existing_columns(table)
            if name in cols:
                return
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {definition_sql}"))

        # Users table (newer fields)
        if "users" in conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        ).scalars().all():
            add_column_if_missing("users", "is_paid", "is_paid INTEGER DEFAULT 0")
            add_column_if_missing("users", "external_id", "external_id TEXT")
            add_column_if_missing("users", "auth_provider", "auth_provider TEXT")
            add_column_if_missing("users", "full_name", "full_name TEXT")
            add_column_if_missing(
                "users",
                "alert_mercury_retrograde",
                "alert_mercury_retrograde INTEGER DEFAULT 1",
            )
            add_column_if_missing(
                "users",
                "alert_frequency",
                "alert_frequency TEXT DEFAULT 'every_retrograde'",
            )
            add_column_if_missing("users", "last_retrograde_alert", "last_retrograde_alert DATETIME")


_ensure_sqlite_schema()
