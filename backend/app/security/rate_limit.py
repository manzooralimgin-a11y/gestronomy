from __future__ import annotations

import asyncio
import time
from collections import defaultdict

from fastapi import Request

from app.config import settings
from app.shared.events import get_redis

_WINDOW_SECONDS = 60
_fallback_counters: dict[str, tuple[int, float]] = defaultdict(lambda: (0, 0.0))
_fallback_lock = asyncio.Lock()


def get_client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "").strip()
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def get_rate_limit_bucket(request: Request) -> tuple[str, int] | None:
    path = request.url.path
    method = request.method.upper()

    if path.startswith("/api/auth/") and method == "POST":
        return "auth", settings.auth_rate_limit_per_minute

    if path == "/api/qr/order" and method == "POST":
        return "public", settings.public_rate_limit_per_minute

    if path.startswith("/api/billing/receipt/") and method == "GET":
        return "public", settings.public_rate_limit_per_minute

    return None


async def enforce_rate_limit(request: Request) -> tuple[bool, int]:
    bucket = get_rate_limit_bucket(request)
    if bucket is None:
        return True, 0

    bucket_name, limit = bucket
    identifier = get_client_identifier(request)
    key = f"rl:{bucket_name}:{identifier}"

    try:
        redis = await get_redis()
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, _WINDOW_SECONDS)
        if count > limit:
            ttl = await redis.ttl(key)
            retry_after = max(ttl, 1) if ttl is not None else 1
            return False, retry_after
        return True, 0
    except Exception:
        # Fallback to in-memory limiter if Redis is unavailable.
        async with _fallback_lock:
            now = time.monotonic()
            count, reset_at = _fallback_counters[key]
            if now >= reset_at:
                count = 0
                reset_at = now + _WINDOW_SECONDS
            count += 1
            _fallback_counters[key] = (count, reset_at)
            if count > limit:
                return False, max(int(reset_at - now), 1)
            return True, 0

