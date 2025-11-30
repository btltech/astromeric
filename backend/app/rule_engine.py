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
    PLANET_SIGN_MEANINGS,
    PLANET_HOUSE_MEANINGS,
    ASPECT_MEANINGS,
    HOUSE_THEMES,
    NUMEROLOGY_MEANINGS,
)


ANGULAR_HOUSES = {1, 4, 7, 10}


def _angular_boost(house: Optional[int]) -> float:
    return 1.2 if house in ANGULAR_HOUSES else 1.0


def _apply_weight(base: float, extra: float) -> float:
    return round(base * extra, 3)


def _aspect_weight(aspect_type: str, orb: float) -> float:
    max_orb = {"conjunction": 7, "opposition": 7, "trine": 5.5, "square": 5.5, "sextile": 3.5}.get(aspect_type, 6)
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
    ) -> Dict:
        blocks: List[Dict] = []
        topic_scores: Dict[str, float] = {}

        # Natal factors
        blocks += self._planet_sign_blocks(chart)
        blocks += self._planet_house_blocks(chart)
        blocks += self._aspect_blocks(chart)

        # Transit to natal for daily/weekly
        if query_type in ["daily_forecast", "weekly_forecast"] and comparison_chart:
            blocks += self._cross_aspect_blocks(
                comparison_chart,
                chart,
                origin="transit",
                planet_filter=transit_planet_filter,
                priority_pairs=synastry_priority,
            )

        # Compatibility synastry
        if query_type.startswith("compatibility") and comparison_chart:
            blocks += self._cross_aspect_blocks(
                chart,
                comparison_chart,
                origin="synastry",
                priority_pairs=synastry_priority,
            )

        # Numerology
        if numerology:
            blocks += self._numerology_blocks(numerology)

        # Aggregate topic scores
        for b in blocks:
            for topic, val in b.get("weights", {}).items():
                topic_scores[topic] = topic_scores.get(topic, 0.0) + val * b.get("weight", 1.0)

        top_themes = sorted(blocks, key=lambda b: b.get("weight", 0), reverse=True)[:5]

        return {
            "topic_scores": topic_scores,
            "selected_blocks": blocks,
            "top_themes": top_themes,
        }

    def _planet_sign_blocks(self, chart: Dict) -> List[Dict]:
        blocks = []
        for p in chart["planets"]:
            meaning = PLANET_SIGN_MEANINGS.get(p["name"], {}).get(p["sign"])
            if not meaning:
                continue
            weight = _angular_boost(p.get("house"))
            blocks.append({**meaning, "weight": weight, "source": f"{p['name']} in {p['sign']}"})
        return blocks

    def _planet_house_blocks(self, chart: Dict) -> List[Dict]:
        blocks = []
        for p in chart["planets"]:
            meaning = PLANET_HOUSE_MEANINGS.get(p["name"], {}).get(p.get("house"))
            if meaning:
                weight = _angular_boost(p.get("house"))
                blocks.append({**meaning, "weight": weight, "source": f"{p['name']} house {p.get('house')}"})
            house_meaning = HOUSE_THEMES.get(p.get("house"))
            if house_meaning:
                blocks.append({**house_meaning, "weight": 0.3, "source": f"House {p.get('house')}"})
        return blocks

    def _aspect_blocks(self, chart: Dict) -> List[Dict]:
        blocks = []
        for asp in chart.get("aspects", []):
            meaning = _aspect_meaning(asp["planet_a"], asp["planet_b"], asp["type"])
            if not meaning:
                continue
            weight = _aspect_weight(asp["type"], asp["orb"])
            blocks.append({**meaning, "weight": weight, "source": f"{asp['planet_a']} {asp['type']} {asp['planet_b']}"})
        return blocks

    def _cross_aspect_blocks(
        self,
        chart_a: Dict,
        chart_b: Dict,
        origin: str,
        planet_filter: Optional[List[str]] = None,
        priority_pairs: Optional[List[str]] = None,
    ) -> List[Dict]:
        blocks = []
        # Build quick lookup by planet name
        positions = {p["name"]: p for p in chart_a["planets"]}
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
                meaning = _aspect_meaning(p_a_name, p_b["name"], aspect_type)
                if not meaning:
                    continue
                base_weight = _aspect_weight(aspect_type, orb) * _angular_boost(p_a.get("house"))
                # Priority synastry weighting
                pair_key = f"{p_a_name}-{p_b['name']}"
                if priority_pairs and pair_key in priority_pairs:
                    base_weight *= 1.2
                blocks.append(
                    {
                        **meaning,
                        "weight": base_weight,
                        "source": f"{origin}:{p_a_name} {aspect_type} {p_b['name']}",
                    }
                )
        return blocks

    def _numerology_blocks(self, numerology: Dict) -> List[Dict]:
        blocks = []
        for key, meaning in NUMEROLOGY_MEANINGS.items():
            val = numerology.get("core_numbers", {}).get(key) or numerology.get("cycles", {}).get(key)
            if val:
                blocks.append({**meaning, "weight": 1.0, "source": f"numerology:{key}={val}"})
        return blocks


def _deg_diff(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def _closest_aspect(diff: float):
    angles = {"conjunction": 0, "sextile": 60, "square": 90, "trine": 120, "opposition": 180}
    orbs = {"conjunction": 7.0, "sextile": 3.5, "square": 5.5, "trine": 5.5, "opposition": 7.0}
    closest = None
    min_orb = 999.0
    for name, angle in angles.items():
        orb = abs(diff - angle)
        if orb < min_orb and orb <= orbs[name]:
            min_orb = orb
            closest = name
    return closest, min_orb


def _aspect_meaning(pa: str, pb: str, aspect_type: str) -> Optional[Dict]:
    pair_key = (pa, pb, aspect_type)
    reverse_key = (pb, pa, aspect_type)
    if pair_key in ASPECT_MEANINGS:
        return ASPECT_MEANINGS[pair_key]
    if reverse_key in ASPECT_MEANINGS:
        return ASPECT_MEANINGS[reverse_key]
    return ASPECT_MEANINGS.get(aspect_type)
