"""One free AI answer a day for website visitors.

The owner's own device uses AI through the access code (``has_ai_access``).
Everyone else on the website gets one Gemini answer a day; after that, and for
everyone once Gemini's free daily quota runs out, answers come from the
built-in guide until the day resets.

A visitor counts as the same person when any of these match an earlier answer
from the same day:

- the device ID the website stores in the browser (``X-Device-Id``);
- the browser signature (``X-Device-Signature``) seen from the same IP address,
  which catches clearing browser data without changing network;
- the signed-in account, when there is one.

A browser signature alone is not used, because identical phones share one, and
an IP alone is not used, because mobile networks put thousands of people behind
one address. Browsers do not let a website read a hardware or MAC address.

Only keyed hashes of these values are stored, and only for the current and
previous day. The day follows Pacific time because Gemini's free quota resets
at midnight there.
"""

from __future__ import annotations

import hashlib
import hmac
import ipaddress
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import Request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .ai_service import has_ai_access, is_native_app
from .exceptions import StructuredLogger
from .middleware.rate_limit import get_client_ip
from .models import FreeAIClaim, SessionLocal

logger = StructuredLogger(__name__)

QUOTA_TZ = ZoneInfo("America/Los_Angeles")
DEVICE_HEADER = "x-device-id"
SIGNATURE_HEADER = "x-device-signature"
# Stored when Gemini says its free daily quota is used up, so nobody else is
# offered an answer until the day resets.
POOL_EXHAUSTED_KEY = "pool:exhausted"
_TOKEN = re.compile(r"^[A-Za-z0-9_-]{16,128}$")

# Statuses sent to the website.
AVAILABLE = "available"  # the visitor has not had today's answer yet
ANSWERED = "answered"  # this reply was the visitor's free AI answer
USED = "used"  # today's answer was already used
POOL_EMPTY = "pool_empty"  # today's free answers have all gone
UNAVAILABLE = "unavailable"  # AI failed this time; the answer is still unused


@dataclass(frozen=True)
class FreeAIState:
    status: str
    resets_at: datetime
    claim_id: Optional[str] = None

    @property
    def granted(self) -> bool:
        return self.claim_id is not None

    def public(self) -> dict:
        return {"status": self.status, "resets_at": self.resets_at.isoformat()}


def quota_day(now: Optional[datetime] = None) -> str:
    now = now or datetime.now(timezone.utc)
    return now.astimezone(QUOTA_TZ).date().isoformat()


def resets_at(now: Optional[datetime] = None) -> datetime:
    now = now or datetime.now(timezone.utc)
    local = now.astimezone(QUOTA_TZ)
    midnight = datetime.combine(
        local.date() + timedelta(days=1), datetime.min.time(), QUOTA_TZ
    )
    return midnight.astimezone(timezone.utc)


def _daily_cap() -> Optional[int]:
    """Optional extra cap on answers a day (FREE_AI_DAILY_LIMIT)."""
    raw = os.getenv("FREE_AI_DAILY_LIMIT", "").strip()
    try:
        cap = int(raw)
    except ValueError:
        return None
    return cap if cap >= 0 else None


def _hash_secret() -> bytes:
    secret = os.getenv("FREE_AI_HASH_KEY", "").strip()
    if not secret:
        from .auth import SECRET_KEY

        secret = SECRET_KEY
    return secret.encode()


def _hash(kind: str, value: str) -> str:
    digest = hmac.new(_hash_secret(), f"{kind}:{value}".encode(), hashlib.sha256)
    return f"{kind}:{digest.hexdigest()[:64]}"


def _network(ip: str) -> str:
    """The whole address for IPv4; the /64 a household gets for IPv6."""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ip
    if addr.version == 6:
        return str(ipaddress.ip_network(f"{ip}/64", strict=False))
    return str(addr)


def _account_id(request: Request) -> Optional[str]:
    auth = request.headers.get("authorization", "")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    from .auth import decode_token

    data = decode_token(token.strip())
    return str(data.user_id) if data and data.user_id else None


def _token(request: Request, header: str) -> Optional[str]:
    value = request.headers.get(header, "").strip()
    return value if _TOKEN.match(value) else None


def visitor_keys(request: Request) -> list[str]:
    """Hashed identifiers for this visitor; empty without a device ID."""
    device = _token(request, DEVICE_HEADER)
    if not device:
        return []
    keys = [_hash("device", device)]
    signature = _token(request, SIGNATURE_HEADER)
    if signature:
        keys.append(_hash("browser", f"{signature}|{_network(get_client_ip(request))}"))
    user_id = _account_id(request)
    if user_id:
        keys.append(_hash("account", user_id))
    return keys


def is_offered(request: Request) -> bool:
    """Free answers are for website visitors; the apps and the owner are not."""
    return not is_native_app(request) and not has_ai_access(request)


def _state_for(db, keys: list[str], day: str) -> str:
    rows = {
        row.key
        for row in db.query(FreeAIClaim.key)
        .filter(
            FreeAIClaim.day == day, FreeAIClaim.key.in_(keys + [POOL_EXHAUSTED_KEY])
        )
        .all()
    }
    if POOL_EXHAUSTED_KEY in rows:
        return POOL_EMPTY
    if rows:
        return USED
    cap = _daily_cap()
    if cap is not None:
        given = (
            db.query(func.count(func.distinct(FreeAIClaim.claim_id)))
            .filter(FreeAIClaim.day == day, FreeAIClaim.key != POOL_EXHAUSTED_KEY)
            .scalar()
        )
        if given >= cap:
            return POOL_EMPTY
    return AVAILABLE


def check(request: Request) -> FreeAIState:
    """What this visitor would get now, without using anything up."""
    reset = resets_at()
    keys = visitor_keys(request)
    if not keys:
        return FreeAIState(USED, reset)
    db = SessionLocal()
    try:
        return FreeAIState(_state_for(db, keys, quota_day()), reset)
    except SQLAlchemyError as e:
        logger.warning(f"Free AI check failed: {type(e).__name__}")
        return FreeAIState(UNAVAILABLE, reset)
    finally:
        db.close()


def claim(request: Request) -> FreeAIState:
    """Reserve today's answer for this visitor before calling the AI.

    Reserving first means two requests sent at once cannot both get one.
    """
    reset = resets_at()
    keys = visitor_keys(request)
    if not keys:
        return FreeAIState(USED, reset)
    day = quota_day()
    db = SessionLocal()
    try:
        # Keep only today's and yesterday's rows.
        cutoff = (datetime.fromisoformat(day) - timedelta(days=1)).date().isoformat()
        db.query(FreeAIClaim).filter(FreeAIClaim.day < cutoff).delete(
            synchronize_session=False
        )
        status = _state_for(db, keys, day)
        if status != AVAILABLE:
            db.commit()
            return FreeAIState(status, reset)
        claim_id = uuid.uuid4().hex
        db.add_all(FreeAIClaim(day=day, key=k, claim_id=claim_id) for k in keys)
        db.commit()
        return FreeAIState(ANSWERED, reset, claim_id)
    except IntegrityError:
        db.rollback()
        return FreeAIState(USED, reset)
    except SQLAlchemyError as e:
        db.rollback()
        logger.warning(f"Free AI claim failed: {type(e).__name__}")
        return FreeAIState(UNAVAILABLE, reset)
    finally:
        db.close()


def _release(db, claim_id: str) -> None:
    db.query(FreeAIClaim).filter(FreeAIClaim.claim_id == claim_id).delete(
        synchronize_session=False
    )


def settle(state: FreeAIState, answered: bool, daily_quota_hit: bool) -> FreeAIState:
    """Keep the reservation if the AI answered; otherwise give it back.

    When Gemini reports its daily quota is used up, today's pool is closed.
    """
    if not state.granted or answered:
        return state
    db = SessionLocal()
    try:
        _release(db, state.claim_id)
        if daily_quota_hit:
            db.add(
                FreeAIClaim(day=quota_day(), key=POOL_EXHAUSTED_KEY, claim_id="pool")
            )
        db.commit()
    except IntegrityError:
        db.rollback()  # another request already closed the pool
        db2 = SessionLocal()
        try:
            _release(db2, state.claim_id)
            db2.commit()
        finally:
            db2.close()
    except SQLAlchemyError as e:
        db.rollback()
        logger.warning(f"Free AI release failed: {type(e).__name__}")
    finally:
        db.close()
    return FreeAIState(POOL_EMPTY if daily_quota_hit else UNAVAILABLE, state.resets_at)
