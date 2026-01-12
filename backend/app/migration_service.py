"""
migration_service.py
Service for migrating anonymous readings to user account on signup
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .models import User, Reading, Profile as DBProfile


def migrate_anon_readings(
    db: Session,
    user: User,
    anon_readings: List[Dict[str, Any]],
    primary_profile_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Migrate anonymous readings to user account.
    
    Args:
        db: Database session
        user: The user account to migrate readings to
        anon_readings: List of anonymous reading dicts from localStorage
        primary_profile_id: Optional profile_id to associate with migrated readings
    
    Returns:
        Migration summary with count of migrated readings
    """
    migrated_count = 0
    failed_readings = []

    for anon_reading in anon_readings:
        try:
            # Extract data
            scope = anon_reading.get("scope", "daily")
            content = anon_reading.get("content", {})
            date_str = anon_reading.get("date")
            
            # Parse date or use current date
            if date_str:
                try:
                    reading_date = datetime.fromisoformat(date_str).date()
                except (ValueError, TypeError):
                    reading_date = datetime.now().date()
            else:
                reading_date = datetime.now().date()

            # Create Reading record
            reading = Reading(
                user_id=user.id,
                profile_id=primary_profile_id,  # Optional: link to primary profile if provided
                scope=scope,
                content=content,
                date=reading_date,
            )
            db.add(reading)
            migrated_count += 1

        except Exception as e:
            failed_readings.append({
                "reading": anon_reading,
                "error": str(e),
            })

    # Commit all successful migrations
    if migrated_count > 0:
        db.commit()

    return {
        "status": "success",
        "migrated_count": migrated_count,
        "failed_count": len(failed_readings),
        "failed_readings": failed_readings if failed_readings else None,
    }


def sync_anon_profile_to_account(
    db: Session,
    user: User,
    anon_profile: Dict[str, Any],
) -> Optional[DBProfile]:
    """
    Create a user profile from anonymous profile data.
    
    Args:
        db: Database session
        user: User to create profile for
        anon_profile: Anonymous profile dict
    
    Returns:
        Created DBProfile or None if failed
    """
    try:
        profile = DBProfile(
            user_id=user.id,
            name=anon_profile.get("name", "Imported Profile"),
            date_of_birth=anon_profile.get("date_of_birth"),
            time_of_birth=anon_profile.get("time_of_birth", "12:00:00"),
            place_of_birth=anon_profile.get("place_of_birth", ""),
            latitude=anon_profile.get("latitude", 0.0),
            longitude=anon_profile.get("longitude", 0.0),
            timezone=anon_profile.get("timezone", "UTC"),
            house_system="placidus",  # Default house system
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    except Exception as e:
        print(f"Error creating profile: {e}")
        return None
