"""
V1 Learn/Learning Router
API v1 learning endpoints (zodiac, numerology, courses, modules)
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(tags=["Learn"])


@router.get("/learn/zodiac")
def learn_zodiac(
    limit: int = Query(default=None, ge=1, le=50, description="Max items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
):
    """Get zodiac glossary with optional pagination."""
    from ..engine.glossary import ZODIAC_GLOSSARY

    items = list(ZODIAC_GLOSSARY.items())
    total = len(items)

    if limit is not None:
        # Return paginated response
        paginated_items = items[offset : offset + limit]
        return {
            "items": [{"key": k, "data": v} for k, v in paginated_items],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
        }

    # Return full glossary for backward compatibility
    return ZODIAC_GLOSSARY


@router.get("/learn/numerology")
def learn_numerology(
    limit: int = Query(default=None, ge=1, le=50, description="Max items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
):
    """Get numerology glossary with optional pagination."""
    from ..engine.glossary import NUMEROLOGY_GLOSSARY

    items = list(NUMEROLOGY_GLOSSARY.items())
    total = len(items)

    if limit is not None:
        # Return paginated response
        paginated_items = items[offset : offset + limit]
        return {
            "items": [{"key": k, "data": v} for k, v in paginated_items],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
        }

    # Return full glossary for backward compatibility
    return NUMEROLOGY_GLOSSARY


@router.get("/learn/modules")
def list_learning_modules():
    """List all available learning modules."""
    from ..engine.learning_content import (
        ELEMENTS_AND_MODALITIES,
        MINI_COURSES,
        MOON_SIGNS,
        RETROGRADE_INFO,
        RISING_SIGNS,
    )

    return {
        "modules": [
            {
                "id": "moon_signs",
                "title": "Moon Signs: Your Emotional Self",
                "description": "Discover how your Moon sign shapes your inner world",
                "item_count": len(MOON_SIGNS),
            },
            {
                "id": "rising_signs",
                "title": "Rising Signs: Your Cosmic Mask",
                "description": "Learn how your Ascendant influences first impressions",
                "item_count": len(RISING_SIGNS),
            },
            {
                "id": "elements",
                "title": "Elements & Modalities",
                "description": "Fire, Earth, Air, Water and Cardinal, Fixed, Mutable",
                "item_count": len(ELEMENTS_AND_MODALITIES.get("elements", {}))
                + len(ELEMENTS_AND_MODALITIES.get("modalities", {})),
            },
            {
                "id": "retrogrades",
                "title": "Planetary Retrogrades",
                "description": "What happens when planets appear to move backward",
                "item_count": len(RETROGRADE_INFO),
            },
            {
                "id": "courses",
                "title": "Mini Courses",
                "description": "Structured lessons for deeper learning",
                "item_count": len(MINI_COURSES),
            },
        ]
    }


@router.get("/learn/module/{module_id}")
def get_module_content(module_id: str):
    """Get full content for a learning module."""
    from ..engine.learning_content import get_learning_module

    content = get_learning_module(module_id)
    if not content:
        raise HTTPException(status_code=404, detail="Module not found")
    return content


@router.get("/learn/course/{course_id}")
def get_course_content(course_id: str):
    """Get a specific mini course with all lessons."""
    from ..engine.learning_content import MINI_COURSES

    course = MINI_COURSES.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/learn/course/{course_id}/lesson/{lesson_number}")
def get_lesson_content(course_id: str, lesson_number: int):
    """Get a specific lesson from a mini course."""
    from ..engine.learning_content import get_lesson

    lesson = get_lesson(course_id, lesson_number)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson
