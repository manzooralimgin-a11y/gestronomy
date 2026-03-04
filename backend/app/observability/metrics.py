from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from redis.asyncio import Redis

from app.config import settings


@dataclass
class RequestSample:
    timestamp: datetime
    path: str
    method: str
    status_code: int
    latency_ms: int


class ApiMetricsCollector:
    def __init__(self, max_samples: int = 20_000) -> None:
        self._samples: deque[RequestSample] = deque(maxlen=max_samples)
        self._lock = asyncio.Lock()

    async def record(
        self,
        *,
        path: str,
        method: str,
        status_code: int,
        latency_ms: int,
    ) -> None:
        async with self._lock:
            self._samples.append(
                RequestSample(
                    timestamp=datetime.now(timezone.utc),
                    path=path,
                    method=method,
                    status_code=status_code,
                    latency_ms=latency_ms,
                )
            )

    async def snapshot(self, window_minutes: int = 15) -> dict:
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=window_minutes)
        async with self._lock:
            rows = [row for row in self._samples if row.timestamp >= window_start]

        total_requests = len(rows)
        if total_requests == 0:
            return {
                "window_minutes": window_minutes,
                "total_requests": 0,
                "p95_latency_ms": 0.0,
                "error_rate_pct": 0.0,
            }

        latencies = sorted(float(row.latency_ms) for row in rows)
        p95_index = max(0, min(len(latencies) - 1, int(len(latencies) * 0.95) - 1))
        p95_latency_ms = latencies[p95_index]
        error_count = sum(1 for row in rows if row.status_code >= 500)
        error_rate_pct = (error_count / total_requests) * 100.0

        return {
            "window_minutes": window_minutes,
            "total_requests": total_requests,
            "p95_latency_ms": round(p95_latency_ms, 2),
            "error_rate_pct": round(error_rate_pct, 3),
        }


api_metrics = ApiMetricsCollector()


def _queue_name_from_broker_url() -> str:
    # Celery default queue name unless custom routing is configured.
    return "celery"


async def get_queue_lag() -> int | None:
    queue_name = _queue_name_from_broker_url()
    parsed = urlparse(settings.celery_broker_url)
    if parsed.scheme not in {"redis", "rediss"}:
        return None

    redis_client = Redis.from_url(settings.celery_broker_url, decode_responses=True)
    try:
        lag = await redis_client.llen(queue_name)
        return int(lag)
    except Exception:
        return None
    finally:
        await redis_client.aclose()
