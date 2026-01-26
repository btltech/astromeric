"""
API v2 Routers
--------------
Standardized router modules following consistent patterns for validation,
error handling, and response formatting.

V2 Routers (Current):
- auth: Authentication (register, login, user management)
- profiles: User profile CRUD operations
- natal: Natal profile and chart calculations
- forecasts: Daily, weekly, monthly forecasts
- compatibility: Relationship and friendship compatibility
- numerology: Numerology analysis and insights
- charts: Raw natal chart and synastry data
- daily_features: Daily affirmations, tarot, moon phases, yes/no guidance
- moon: Moon phases and rituals
- timing: Best times for activities
- relationships: Love and relationship timing
- journal: Reading journal and accountability
- habits: Habit tracking with lunar cycles
- year_ahead: Year-ahead forecasts
- transits: Daily transit alerts
- ai: AI-powered explanations
- cosmic_guide: AI chat for cosmic wisdom
- learning: Educational content
- feedback: Section feedback
- system: Health checks and debug endpoints

V1 Routers (Legacy - Deprecated):
- v1_auth, v1_profiles, v1_readings, v1_learning, v1_moon, v1_timing,
- v1_journal, v1_relationships, v1_habits, v1_numerology, v1_ai
"""

# V2 Routers
from . import (
    ai,
    alerts,
    auth,
    charts,
    compatibility,
    cosmic_guide,
    daily_features,
    feedback,
    forecasts,
    habits,
    journal,
    learning,
    moon,
    natal,
    numerology,
    profiles,
    relationships,
    sky,
    system,
    timing,
    transits,
    year_ahead,
)

# V1 Legacy Routers (deprecated)
from . import (
    v1_ai,
    v1_auth,
    v1_habits,
    v1_journal,
    v1_learning,
    v1_moon,
    v1_numerology,
    v1_profiles,
    v1_readings,
    v1_relationships,
    v1_timing,
)

__all__ = [
    # V2
    "ai",
    "alerts",
    "auth",
    "charts",
    "compatibility",
    "cosmic_guide",
    "daily_features",
    "feedback",
    "forecasts",
    "habits",
    "journal",
    "learning",
    "moon",
    "natal",
    "numerology",
    "profiles",
    "relationships",
    "sky",
    "system",
    "timing",
    "transits",
    "year_ahead",
    # V1 Legacy
    "v1_ai",
    "v1_auth",
    "v1_habits",
    "v1_journal",
    "v1_learning",
    "v1_moon",
    "v1_numerology",
    "v1_profiles",
    "v1_readings",
    "v1_relationships",
    "v1_timing",
]
