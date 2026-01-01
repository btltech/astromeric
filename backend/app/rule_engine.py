"""
rule_engine.py
--------------
Selects relevant chart and numerology factors, weights them, and aggregates themes.

Outputs:
{
  "topic_scores": {...},
  "selected_blocks": [...],
  "top_themes": [...]
}
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .interpretation import (
    ASPECT_MEANINGS,
    HOUSE_THEMES,
    NUMEROLOGY_MEANINGS,
    PLANET_HOUSE_MEANINGS,
    PLANET_SIGN_MEANINGS,
    get_planet_sign_text,
    get_planet_sign_meanings,
    get_planet_house_meanings,
    get_aspect_meanings,
    get_numerology_meanings,
    get_house_themes,
)

ANGULAR_HOUSES = {1, 4, 7, 10}


def _angular_boost(house: Optional[int]) -> float:
    return 1.2 if house in ANGULAR_HOUSES else 1.0


def _apply_weight(base: float, extra: float) -> float:
    return round(base * extra, 3)


def _aspect_weight(aspect_type: str, orb: float) -> float:
    max_orb = {
        "conjunction": 7,
        "opposition": 7,
        "trine": 5.5,
        "square": 5.5,
        "sextile": 3.5,
    }.get(aspect_type, 6)
    proximity = max(0.1, 1 - orb / max_orb)
    type_boost = 1.2 if aspect_type in ["conjunction", "opposition"] else 1.0
    type_boost = 1.1 if aspect_type in ["trine", "sextile"] else type_boost
    return round(proximity * type_boost, 3)


class RuleEngine:
    def evaluate(
        self,
        query_type: str,
        chart: Dict,
        numerology: Optional[Dict] = None,
        comparison_chart: Optional[Dict] = None,
        transit_planet_filter: Optional[List[str]] = None,
        synastry_priority: Optional[List[str]] = None,
        lang: str = "en",
    ) -> Dict:
        blocks: List[Dict] = []
        topic_scores: Dict[str, float] = {}

        # Get localized meanings
        planet_sign_meanings = get_planet_sign_meanings(lang)
        planet_house_meanings = get_planet_house_meanings(lang)
        house_themes = get_house_themes(lang)
        aspect_meanings = get_aspect_meanings(lang)
        numerology_meanings = get_numerology_meanings(lang)

        # Natal factors
        blocks += self._planet_sign_blocks(chart, query_type, planet_sign_meanings, lang)
        blocks += self._planet_house_blocks(chart, planet_house_meanings, house_themes)
        blocks += self._aspect_blocks(chart, aspect_meanings)

        # Transit to natal for daily/weekly/monthly forecasts
        if query_type in ["daily_forecast", "weekly_forecast", "monthly_forecast"] and comparison_chart:
            blocks += self._cross_aspect_blocks(
                comparison_chart,
                chart,
                origin="transit",
                planet_filter=transit_planet_filter,
                priority_pairs=synastry_priority,
                scope=query_type,  # Pass scope for weighting
                aspect_meanings=aspect_meanings,
            )

        # Compatibility synastry
        if query_type.startswith("compatibility") and comparison_chart:
            blocks += self._cross_aspect_blocks(
                chart,
                comparison_chart,
                origin="synastry",
                priority_pairs=synastry_priority,
                aspect_meanings=aspect_meanings,
            )

        # Numerology
        if numerology:
            blocks += self._numerology_blocks(numerology, numerology_meanings)

        # Aggregate topic scores
        for b in blocks:
            for topic, val in b.get("weights", {}).items():
                topic_scores[topic] = topic_scores.get(topic, 0.0) + val * b.get(
                    "weight", 1.0
                )

        top_themes = sorted(blocks, key=lambda b: b.get("weight", 0), reverse=True)[:5]

        return {
            "topic_scores": topic_scores,
            "selected_blocks": blocks,
            "top_themes": top_themes,
        }

    def _planet_sign_blocks(self, chart: Dict, query_type: str = "", planet_sign_meanings: Dict = {}, lang: str = "en") -> List[Dict]:
        blocks = []
        # Scope-specific planet emphasis
        # Daily: fast planets matter more (Moon, Mercury, Sun)
        # Weekly: medium planets (Venus, Mars) 
        # Monthly: slow planets (Jupiter, Saturn, outer)
        scope_weights = {
            "daily_forecast": {"Moon": 1.5, "Mercury": 1.3, "Sun": 1.2, "Venus": 1.0, "Mars": 0.9},
            "weekly_forecast": {"Mars": 1.4, "Venus": 1.3, "Sun": 1.1, "Mercury": 1.0, "Moon": 0.8},
            "monthly_forecast": {"Jupiter": 1.5, "Saturn": 1.4, "Pluto": 1.3, "Neptune": 1.2, "Uranus": 1.2, "Mars": 1.0},
        }
        weights = scope_weights.get(query_type, {})
        
        for p in chart["planets"]:
            meaning = planet_sign_meanings.get(p["name"], {}).get(p["sign"])
            if not meaning:
                continue
            weight = _angular_boost(p.get("house"))
            # Apply scope-specific planet weighting
            planet_emphasis = weights.get(p["name"], 1.0)
            weight *= planet_emphasis
            # Generate fresh, readable text instead of static template
            fresh_text = get_planet_sign_text(p["name"], p["sign"], lang)
            blocks.append(
                {
                    **meaning,
                    "text": fresh_text,
                    "weight": weight,
                    "source": f"{p['name']} in {p['sign']}",
                }
            )
        return blocks

    def _planet_house_blocks(self, chart: Dict, planet_house_meanings: Dict = {}, house_themes: Dict = {}) -> List[Dict]:
        blocks = []
        for p in chart["planets"]:
            meaning = planet_house_meanings.get(p["name"], {}).get(p.get("house"))
            if meaning:
                weight = _angular_boost(p.get("house"))
                blocks.append(
                    {
                        **meaning,
                        "weight": weight,
                        "source": f"{p['name']} house {p.get('house')}",
                    }
                )
            house_meaning = house_themes.get(p.get("house"))
            if house_meaning:
                blocks.append(
                    {
                        **house_meaning,
                        "weight": 0.3,
                        "source": f"House {p.get('house')}",
                    }
                )
        return blocks

    def _aspect_blocks(self, chart: Dict, aspect_meanings: Dict = {}) -> List[Dict]:
        blocks = []
        for asp in chart.get("aspects", []):
            meaning = _aspect_meaning(asp["planet_a"], asp["planet_b"], asp["type"], aspect_meanings)
            if not meaning:
                continue
            weight = _aspect_weight(asp["type"], asp["orb"])
            blocks.append(
                {
                    **meaning,
                    "weight": weight,
                    "source": f"{asp['planet_a']} {asp['type']} {asp['planet_b']}",
                }
            )
        return blocks

    def _cross_aspect_blocks(
        self,
        chart_a: Dict,
        chart_b: Dict,
        origin: str,
        planet_filter: Optional[List[str]] = None,
        priority_pairs: Optional[List[str]] = None,
        scope: str = "",
        aspect_meanings: Dict = {},
    ) -> List[Dict]:
        blocks = []
        # Scope-specific transit planet emphasis
        transit_weights = {
            "daily_forecast": {"Moon": 1.8, "Mercury": 1.4, "Sun": 1.3, "Venus": 1.1, "Mars": 1.0, "Jupiter": 0.8, "Saturn": 0.8},
            "weekly_forecast": {"Mars": 1.5, "Venus": 1.4, "Mercury": 1.2, "Sun": 1.1, "Jupiter": 1.3, "Saturn": 1.3, "Moon": 0.6},
            "monthly_forecast": {"Jupiter": 1.6, "Saturn": 1.5, "Uranus": 1.4, "Neptune": 1.3, "Pluto": 1.3, "Mars": 1.1, "Venus": 1.0, "Sun": 0.9, "Moon": 0.5},
        }
        scope_weights = transit_weights.get(scope, {})
        
        # Build quick lookup by planet name
        positions = {p["name"]: p for p in chart_a["planets"]}
        priority_lookup = set(priority_pairs or [])
        for p_b in chart_b["planets"]:
            if planet_filter and p_b["name"] not in planet_filter:
                continue
            for p_a_name, p_a in positions.items():
                if planet_filter and p_a_name not in planet_filter:
                    continue
                diff = _deg_diff(p_a["absolute_degree"], p_b["absolute_degree"])
                aspect_type, orb = _closest_aspect(diff)
                if not aspect_type:
                    continue
                meaning = _aspect_meaning(p_a_name, p_b["name"], aspect_type, aspect_meanings)
                if not meaning:
                    continue
                base_weight = _aspect_weight(aspect_type, orb) * _angular_boost(
                    p_a.get("house")
                )
                # Apply scope-specific transit planet emphasis
                transit_planet_emphasis = scope_weights.get(p_a_name, 1.0)
                base_weight *= transit_planet_emphasis
                
                # Priority synastry weighting
                pair_key = f"{p_a_name}-{p_b['name']}"
                reverse_pair = f"{p_b['name']}-{p_a_name}"
                if priority_lookup and (
                    pair_key in priority_lookup or reverse_pair in priority_lookup
                ):
                    base_weight *= 1.2
                
                # Human-readable source label
                if origin == "transit":
                    source_label = f"Transit {p_a_name} {aspect_type} natal {p_b['name']}"
                elif origin == "synastry":
                    source_label = f"{p_a_name} {aspect_type} {p_b['name']} (synastry)"
                else:
                    source_label = f"{p_a_name} {aspect_type} {p_b['name']}"
                
                blocks.append(
                    {
                        **meaning,
                        "weight": base_weight,
                        "source": source_label,
                    }
                )
        return blocks

    def _numerology_blocks(self, numerology: Dict, numerology_meanings: Dict = {}) -> List[Dict]:
        """Generate interpretation blocks from numerology data."""
        blocks = []
        added = set()
        
        # Human-readable names for numerology types
        type_names = {
            "life_path": "Life Path",
            "expression": "Expression",
            "soul_urge": "Soul Urge", 
            "personality": "Personality",
            "personal_year": "Personal Year",
            "personal_month": "Personal Month",
            "personal_day": "Personal Day",
        }
        
        for entry in numerology.get("meaning_blocks", []):
            etype = entry.get("type")
            value = entry.get("value")
            if not etype or value is None:
                continue
            
            # Skip base type blocks - only use specific numbered ones to avoid redundancy
            # e.g., skip "soul_urge" generic, only include "Soul Urge 6"
            specific = numerology_meanings.get(f"{etype}_{value}")
            if specific:
                human_name = type_names.get(etype, etype.replace("_", " ").title())
                blocks.append({
                    **specific, 
                    "weight": 1.0, 
                    "source": f"{human_name} {value}"
                })
                added.add(f"{etype}_{value}")
        
        return blocks


def _deg_diff(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def _closest_aspect(diff: float):
    angles = {
        "conjunction": 0,
        "sextile": 60,
        "square": 90,
        "trine": 120,
        "opposition": 180,
    }
    orbs = {
        "conjunction": 7.0,
        "sextile": 3.5,
        "square": 5.5,
        "trine": 5.5,
        "opposition": 7.0,
    }
    closest = None
    min_orb = 999.0
    for name, angle in angles.items():
        orb = abs(diff - angle)
        if orb < min_orb and orb <= orbs[name]:
            min_orb = orb
            closest = name
    return closest, min_orb


def _aspect_meaning(pa: str, pb: str, aspect_type: str, aspect_meanings: Dict = {}) -> Optional[Dict]:
    """Get aspect meaning, with dynamic fallback for unlisted pairs."""
    pair_key = (pa, pb, aspect_type)
    reverse_key = (pb, pa, aspect_type)
    
    # Check for specific pair meaning first
    if pair_key in aspect_meanings:
        return aspect_meanings[pair_key]
    if reverse_key in aspect_meanings:
        return aspect_meanings[reverse_key]
    
    # Generate dynamic text for unlisted pairs
    base = aspect_meanings.get(aspect_type)
    if not base:
        return None
    
    # Planet themes for evocative dynamic text
    planet_themes = {
        "Sun": "radiant core",
        "Moon": "emotional depths",
        "Mercury": "quicksilver mind",
        "Venus": "heart magnetism",
        "Mars": "warrior flame",
        "Jupiter": "abundance channel",
        "Saturn": "mastery blueprint",
        "Uranus": "lightning insight",
        "Neptune": "mystic waters",
        "Pluto": "phoenix power",
    }
    
    aspect_verbs = {
        "trine": "dances effortlessly with",
        "sextile": "opens doors to",
        "conjunction": "fuses intensely with",
        "square": "wrestles productively with",
        "opposition": "mirrors and balances",
    }
    
    theme_a = planet_themes.get(pa, pa)
    theme_b = planet_themes.get(pb, pb)
    verb = aspect_verbs.get(aspect_type, "weaves into")
    
    # Create dynamic text with correct grammar (plural subject)
    dynamic_text = f"Your {theme_a} {verb} your {theme_b}."
    
    return {
        **base,
        "text": dynamic_text,
    }
