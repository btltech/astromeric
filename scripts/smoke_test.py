#!/usr/bin/env python3
"""
smoke_test.py — live API smoke test for the AstroNumeric backend.

Hits the deployed (or local) backend across read, compute, AI, and mutating
endpoints, asserts HTTP status + basic response shape, and prints a pass/fail
report. Pure standard library — no pip install required.

USAGE
  python3 scripts/smoke_test.py                       # read + compute groups
  python3 scripts/smoke_test.py --include-ai          # also test Gemini-backed
  python3 scripts/smoke_test.py --include-mutating     # also create+delete a profile
  python3 scripts/smoke_test.py --base-url http://localhost:8000
  API_BASE_URL=https://... python3 scripts/smoke_test.py

EXIT CODE
  0 = all executed checks passed
  1 = one or more checks failed

NOTES
  - "read" and "compute" endpoints do not persist data and are safe to run
    against production.
  - "ai" requires GEMINI_API_KEY configured on the server and may be slow.
  - "mutating" creates a throwaway profile and deletes it afterward.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://astromeric-backend-production.up.railway.app"

# Inline birth data reused across compute endpoints (never persisted).
SAMPLE_PROFILE = {
    "name": "Smoke Test",
    "date_of_birth": "1990-06-15",
    "time_of_birth": "14:30:00",
    "time_confidence": "exact",
    "place_of_birth": "New York, NY, USA",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York",
    "house_system": "Placidus",
}
SAMPLE_PROFILE_B = {
    "name": "Smoke Test B",
    "date_of_birth": "1988-11-02",
    "time_of_birth": "09:15:00",
    "time_confidence": "exact",
    "place_of_birth": "London, UK",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London",
    "house_system": "Placidus",
}


class Check:
    def __init__(
        self, name, method, path, *, group, body=None, expect=(200,), validate=None
    ):
        self.name = name
        self.method = method
        self.path = path
        self.group = group
        self.body = body
        self.expect = set(expect)
        self.validate = validate


# ---- Validators -------------------------------------------------------------


def ok_success(payload):
    """Response is a standard ApiResponse with status == success / data present."""
    if not isinstance(payload, dict):
        return False, "not a JSON object"
    if payload.get("status") in ("success", "ok"):
        return True, ""
    if "data" in payload:
        return True, ""
    return False, f"unexpected shape: keys={list(payload)[:6]}"


def chart_has_real_planets(payload):
    """Sky/planet positions should not be the degenerate stub (varied distances)."""
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list) or not data:
        return False, "no planet list"
    distances = {
        round(float(p.get("distance", 0)), 3) for p in data if isinstance(p, dict)
    }
    if len(distances) <= 1:
        return False, "all distances identical (possible stub)"
    return True, ""


def natal_not_degraded(payload):
    """A real natal chart must not be flagged degraded / provider=stub."""
    data = payload.get("data") if isinstance(payload, dict) else {}
    meta = (data or {}).get("metadata", {}) if isinstance(data, dict) else {}
    if meta.get("degraded") is True or meta.get("provider") == "stub":
        return False, f"degraded chart: provider={meta.get('provider')}"
    return True, ""


# ---- Check catalog ----------------------------------------------------------


def build_checks():
    p = {"profile": SAMPLE_PROFILE}
    return [
        # --- read (safe GETs) ---
        Check(
            "health (root)",
            "GET",
            "/health",
            group="read",
            validate=lambda d: (d.get("status") == "ok", ""),
        ),
        Check(
            "system health",
            "GET",
            "/v2/system/health",
            group="read",
            validate=ok_success,
        ),
        Check(
            "system info", "GET", "/v2/system/info", group="read", validate=ok_success
        ),
        Check(
            "sky planets (REAL ephemeris)",
            "GET",
            "/v2/sky/planets",
            group="read",
            validate=chart_has_real_planets,
        ),
        Check("moon phase", "GET", "/v2/moon/phase", group="read", validate=ok_success),
        Check(
            "moon upcoming",
            "GET",
            "/v2/moon/upcoming",
            group="read",
            validate=ok_success,
        ),
        Check(
            "daily moon-phase",
            "GET",
            "/v2/daily/moon-phase",
            group="read",
            validate=ok_success,
        ),
        Check(
            "learning modules",
            "GET",
            "/v2/learning/modules",
            group="read",
            validate=ok_success,
        ),
        Check(
            "learning glossary",
            "GET",
            "/v2/learning/glossary",
            group="read",
            validate=ok_success,
        ),
        Check(
            "learning zodiac/leo",
            "GET",
            "/v2/learning/zodiac/leo",
            group="read",
            validate=ok_success,
        ),
        Check(
            "relationships events",
            "GET",
            "/v2/relationships/events",
            group="read",
            validate=ok_success,
        ),
        Check(
            "relationships phases",
            "GET",
            "/v2/relationships/phases",
            group="read",
            validate=ok_success,
        ),
        Check(
            "relationships venus-status",
            "GET",
            "/v2/relationships/venus-status",
            group="read",
            validate=ok_success,
        ),
        Check(
            "relationships best-days/aries",
            "GET",
            "/v2/relationships/best-days/aries",
            group="read",
            validate=ok_success,
        ),
        Check(
            "timing activities",
            "GET",
            "/v2/timing/activities",
            group="read",
            validate=ok_success,
        ),
        Check(
            "alerts vapid-key",
            "GET",
            "/v2/alerts/vapid-key",
            group="read",
            validate=ok_success,
        ),
        Check("profiles list", "GET", "/v2/profiles/", group="read"),
        Check(
            "journal prompts",
            "GET",
            "/v2/journal/prompts",
            group="read",
            validate=ok_success,
        ),
        # --- compute (POST, inline data, non-persisting) ---
        Check(
            "natal chart",
            "POST",
            "/v2/charts/natal",
            group="compute",
            body={"profile": SAMPLE_PROFILE, "include_aspects": True, "orb": 8.0},
            validate=natal_not_degraded,
        ),
        Check(
            "forecast daily",
            "POST",
            "/v2/forecasts/daily",
            group="compute",
            body={"profile": SAMPLE_PROFILE, "scope": "daily"},
            validate=ok_success,
        ),
        Check(
            "forecast weekly",
            "POST",
            "/v2/forecasts/weekly",
            group="compute",
            body={"profile": SAMPLE_PROFILE, "scope": "weekly"},
            validate=ok_success,
        ),
        Check(
            "forecast monthly",
            "POST",
            "/v2/forecasts/monthly",
            group="compute",
            body={"profile": SAMPLE_PROFILE, "scope": "monthly"},
            validate=ok_success,
        ),
        Check(
            "compatibility romantic",
            "POST",
            "/v2/compatibility/romantic",
            group="compute",
            body={
                "person_a": SAMPLE_PROFILE,
                "person_b": SAMPLE_PROFILE_B,
                "relationship_type": "romantic",
            },
            validate=ok_success,
        ),
        Check(
            "compatibility friendship",
            "POST",
            "/v2/compatibility/friendship",
            group="compute",
            body={
                "person_a": SAMPLE_PROFILE,
                "person_b": SAMPLE_PROFILE_B,
                "relationship_type": "friendship",
            },
            validate=ok_success,
        ),
        Check(
            "numerology core",
            "POST",
            "/v2/numerology/core",
            group="compute",
            body={"profile": SAMPLE_PROFILE, "method": "pythagorean"},
            validate=ok_success,
        ),
        Check(
            "numerology profile",
            "POST",
            "/v2/numerology/profile",
            group="compute",
            body={"profile": SAMPLE_PROFILE, "include_extended": True},
            validate=ok_success,
        ),
        Check(
            "numerology compatibility",
            "POST",
            "/v2/numerology/compatibility",
            group="compute",
            body={"profile": SAMPLE_PROFILE, "person_b": SAMPLE_PROFILE_B},
            validate=ok_success,
        ),
        Check(
            "year-ahead forecast",
            "POST",
            "/v2/year-ahead/forecast",
            group="compute",
            body=p,
            validate=ok_success,
        ),
        Check(
            "year-ahead life-phase",
            "POST",
            "/v2/year-ahead/life-phase",
            group="compute",
            body=SAMPLE_PROFILE,
            validate=ok_success,
        ),
        Check(
            "moon ritual",
            "POST",
            "/v2/moon/ritual",
            group="compute",
            body={"profile": SAMPLE_PROFILE},
            validate=ok_success,
        ),
        Check(
            "transits daily",
            "POST",
            "/v2/transits/daily",
            group="compute",
            body=p,
            validate=ok_success,
        ),
        # --- ai (Gemini-backed; needs GEMINI_API_KEY on server) ---
        Check(
            "cosmic-guide chat",
            "POST",
            "/v2/cosmic-guide/chat",
            group="ai",
            body={
                "message": "What is the general energy of today?",
                "sun_sign": "Gemini",
            },
            expect=(200,),
            validate=ok_success,
        ),
        Check(
            "daily affirmation",
            "POST",
            "/v2/daily/affirmation",
            group="ai",
            body=p,
            validate=ok_success,
        ),
    ]


# ---- HTTP -------------------------------------------------------------------


def request(base_url, check, timeout):
    url = base_url.rstrip("/") + check.path
    data = None
    headers = {"Accept": "application/json"}
    if check.body is not None:
        data = json.dumps(check.body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=check.method)
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        status = e.code
    except Exception as e:  # connection/timeout/etc.
        return None, None, (time.time() - started) * 1000, str(e)
    elapsed = (time.time() - started) * 1000
    parsed = None
    if raw.strip():
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"_raw": raw[:200]}
    return status, parsed, elapsed, None


# ---- Runner -----------------------------------------------------------------


def run(base_url, groups, timeout):
    checks = [c for c in build_checks() if c.group in groups]
    results = {"pass": 0, "fail": 0}
    print(f"\nAstroNumeric API smoke test → {base_url}")
    print(f"Groups: {', '.join(sorted(groups))}\n" + "-" * 72)
    for c in checks:
        status, payload, ms, err = request(base_url, c, timeout)
        if err is not None:
            print(f"FAIL  {c.name:<34} {c.method:<4} {c.path}  ERROR: {err}")
            results["fail"] += 1
            continue
        status_ok = status in c.expect
        detail = ""
        if status_ok and c.validate and payload is not None:
            valid, msg = c.validate(payload)
            status_ok = status_ok and valid
            detail = msg
        elif status_ok and c.validate and payload is None:
            status_ok, detail = False, "empty body"
        tag = "PASS" if status_ok else "FAIL"
        results["pass" if status_ok else "fail"] += 1
        line = f"{tag}  {c.name:<34} {c.method:<4} {c.path}  [{status}] {ms:6.0f}ms"
        if not status_ok and detail:
            line += f"  ← {detail}"
        print(line)
    return results


def run_mutating(base_url, timeout):
    """Create a throwaway profile then delete it (persistence round-trip)."""
    print("-" * 72 + "\nmutating: profile create → delete")
    create = Check(
        "profile create",
        "POST",
        "/v2/profiles/",
        group="mutating",
        body=SAMPLE_PROFILE,
        expect=(200, 201),
    )
    status, payload, ms, err = request(base_url, create, timeout)
    if err or status not in create.expect or not isinstance(payload, dict):
        print(f"FAIL  profile create  [{status}] {err or ''}")
        return {"pass": 0, "fail": 1}
    data = payload.get("data", payload)
    pid = data.get("id") if isinstance(data, dict) else None
    print(f"PASS  profile create  [{status}] {ms:.0f}ms  id={pid}")
    if pid is None:
        print("WARN  no profile id returned; skipping delete")
        return {"pass": 1, "fail": 0}
    delete = Check(
        "profile delete",
        "DELETE",
        f"/v2/profiles/{pid}",
        group="mutating",
        expect=(200, 204),
    )
    status, _, ms, err = request(base_url, delete, timeout)
    ok = (not err) and status in delete.expect
    print(
        f"{'PASS' if ok else 'FAIL'}  profile delete  [{status}] {ms:.0f}ms  (cleanup)"
    )
    return {"pass": 1 + int(ok), "fail": int(not ok)}


def main():
    ap = argparse.ArgumentParser(description="AstroNumeric backend smoke test")
    ap.add_argument("--base-url", default=os.getenv("API_BASE_URL", DEFAULT_BASE_URL))
    ap.add_argument(
        "--include-ai", action="store_true", help="test Gemini-backed endpoints"
    )
    ap.add_argument(
        "--include-mutating", action="store_true", help="create+delete a profile"
    )
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()

    groups = {"read", "compute"}
    if args.include_ai:
        groups.add("ai")

    totals = run(args.base_url, groups, args.timeout)
    if args.include_mutating:
        m = run_mutating(args.base_url, args.timeout)
        totals["pass"] += m["pass"]
        totals["fail"] += m["fail"]

    print("-" * 72)
    print(f"RESULT: {totals['pass']} passed, {totals['fail']} failed")
    sys.exit(1 if totals["fail"] else 0)


if __name__ == "__main__":
    main()
