from backend.app.interpretation import (
    ASPECT_MEANINGS,
    NUMEROLOGY_MEANINGS,
    PLANET_HOUSE_MEANINGS,
    PLANET_SIGN_MEANINGS,
)


def test_planet_sign_full_coverage():
    for planet, signs in PLANET_SIGN_MEANINGS.items():
        assert len(signs) == 12, f"{planet} missing signs"
        for sign, block in signs.items():
            assert "text" in block and "weights" in block


def test_planet_house_full_coverage():
    for planet, houses in PLANET_HOUSE_MEANINGS.items():
        assert len(houses) == 12, f"{planet} missing houses"


def test_aspect_pair_lookup():
    assert ("Sun", "Moon", "conjunction") in ASPECT_MEANINGS
    assert ("Venus", "Mars", "conjunction") in ASPECT_MEANINGS


def test_numerology_number_specific():
    for kind in ["life_path", "expression", "soul_urge"]:
        for num in range(1, 10):
            key = f"{kind}_{num}"
            assert key in NUMEROLOGY_MEANINGS
