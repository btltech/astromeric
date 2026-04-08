"""
constants.py
Shared constants for numerology calculations.
Single source of truth for letter values, vowels, and reduction functions.
"""

from typing import Set

# Pythagorean numerology letter values (1-9 cycle)
LETTER_VALUES = {
    "a": 1,
    "b": 2,
    "c": 3,
    "d": 4,
    "e": 5,
    "f": 6,
    "g": 7,
    "h": 8,
    "i": 9,
    "j": 1,
    "k": 2,
    "l": 3,
    "m": 4,
    "n": 5,
    "o": 6,
    "p": 7,
    "q": 8,
    "r": 9,
    "s": 1,
    "t": 2,
    "u": 3,
    "v": 4,
    "w": 5,
    "x": 6,
    "y": 7,
    "z": 8,
}

# Chaldean numerology letter values (1-8 cycle; 9 is sacred and not assigned to letters)
# Grouped by value for auditability.
# 1: A I J Q Y
# 2: B K R
# 3: C G L S
# 4: D M T
# 5: E H N X
# 6: U V W
# 7: O Z
# 8: F P
CHALDEAN_LETTER_VALUES = {
    "a": 1,
    "i": 1,
    "j": 1,
    "q": 1,
    "y": 1,
    "b": 2,
    "k": 2,
    "r": 2,
    "c": 3,
    "g": 3,
    "l": 3,
    "s": 3,
    "d": 4,
    "m": 4,
    "t": 4,
    "e": 5,
    "h": 5,
    "n": 5,
    "x": 5,
    "u": 6,
    "v": 6,
    "w": 6,
    "o": 7,
    "z": 7,
    "f": 8,
    "p": 8,
}

# Standard vowels for Soul Urge calculation (Y is treated as consonant in Pythagorean system)
VOWELS: Set[str] = {"a", "e", "i", "o", "u"}

# Master numbers that are not reduced
MASTER_NUMBERS = {11, 22, 33}


def reduce_number(num: int, keep_master: bool = True) -> int:
    """
    Reduce a number to a single digit, optionally preserving master numbers.

    Args:
        num: The number to reduce
        keep_master: If True, preserves 11, 22, 33 as master numbers

    Returns:
        Reduced single digit or master number
    """
    master = MASTER_NUMBERS if keep_master else set()
    while num > 9 and num not in master:
        num = sum(int(d) for d in str(num))
    return num
