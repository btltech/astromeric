import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.engine.astrology import get_zodiac_sign, get_element
from app.engine.numerology import calculate_life_path_number, calculate_name_number
from app.engine.fusion import fuse_prediction


def test_zodiac_boundaries():
    assert get_zodiac_sign("1990-03-21") == "Aries"
    assert get_zodiac_sign("1990-04-19") == "Aries"
    assert get_zodiac_sign("1990-04-20") == "Taurus"


def test_numerology_basic():
    assert calculate_life_path_number("1990-01-01") in range(1, 10) or calculate_life_path_number("1990-01-01") in (11,22,33)
    assert isinstance(calculate_name_number("Jane Doe"), int)


def test_fusion_consistency():
    a = fuse_prediction("John Doe", "1990-01-01", "2025-11-30")
    b = fuse_prediction("John Doe", "1990-01-01", "2025-11-30")
    assert a == b
    assert "sign" in a and "tracks" in a and "affirmation" in a
