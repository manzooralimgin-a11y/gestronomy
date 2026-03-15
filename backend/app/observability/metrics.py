from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict
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


@dataclass
class EndpointStats:
    """Per-endpoint aggregate stats."""
    total_requests: int = 0
    total_errors: int = 0
    total_latency_ms: float = 0
    max_latency_ms: float = 0


class ApiMetricsCollector:
    def __init__(self, max_samples: int = 20_000) -> None:
        self._samples: deque[RequestSample] = deque(maxlen=max_samples)
        self._lock = asyncio.Lock()
        self._endpoint_stats: Dict[str, EndpointStats] = {}
        self._total_requests: int = 0
        self._total_errors: int = 0

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
            # Update aggregate counters
            self._total_requests += 1
            if status_code >= 500:
                self._total_errors += 1

            key = f"{method} {path}"
            stats = self._endpoint_stats.setdefault(key, EndpointStats())
            stats.total_requests += 1
            stats.total_latency_ms += latency_ms
            stats.max_latency_ms = max(stats.max_latency_ms, latency_ms)
            if status_code >= 500:
                stats.total_errors += 1

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
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "error_rate_pct": 0.0,
                "avg_latency_ms": 0.0,
            }

        latencies = sorted(float(row.latency_ms) for row in rows)
        p50_index = max(0, min(len(latencies) - 1, int(len(latencies) * 0.50) - 1))
        p95_index = max(0, min(len(latencies) - 1, int(len(latencies) * 0.95) - 1))
        p99_index = max(0, min(len(latencies) - 1, int(len(latencies) * 0.99) - 1))
        error_count = sum(1 for row in rows if row.status_code >= 500)
        error_rate_pct = (error_count / total_requests) * 100.0
        avg_latency = sum(latencies) / total_requests

        # Status code distribution
        status_dist: Dict[str, int] = {}
        for row in rows:
            bucket = f"{row.status_code // 100}xx"
            status_dist[bucket] = status_dist.get(bucket, 0) + 1

        return {
            "window_minutes": window_minutes,
            "total_requests": total_requests,
            "p50_latency_ms": round(latencies[p50_index], 2),
            "p95_latency_ms": round(latencies[p95_index], 2),
            "p99_latency_ms": round(latencies[p99_index], 2),
            "avg_latency_ms": round(avg_latency, 2),
            "error_rate_pct": round(error_rate_pct, 3),
            "status_distribution": status_dist,
        }

    async def top_endpoints(self, limit: int = 10) -> list[dict]:
        """Return top endpoints by request count."""
        async with self._lock:
            sorted_endpoints = sorted(
                self._endpoint_stats.items(),
                key=lambda x: x[1].total_requests,
                reverse=True,
            )[:limit]

        return [
            {
                "endpoint": key,
                "total_requests": stats.total_requests,
                "avg_latency_ms": round(stats.total_latency_ms / max(stats.total_requests, 1), 2),
                "max_latency_ms": round(stats.max_latency_ms, 2),
                "error_rate_pct": round(
                    (stats.total_errors / max(stats.total_requests, 1)) * 100, 2
                ),
            }
            for key, stats in sorted_endpoints
        ]

    async def slowest_endpoints(self, limit: int = 10) -> list[dict]:
        """Return slowest endpoints by average latency."""
        async with self._lock:
            sorted_endpoints = sorted(
                self._endpoint_stats.items(),
                key=lambda x: x[1].total_latency_ms / max(x[1].total_requests, 1),
                reverse=True,
            )[:limit]

        return [
            {
                "endpoint": key,
                "avg_latency_ms": round(stats.total_latency_ms / max(stats.total_requests, 1), 2),
                "max_latency_ms": round(stats.max_latency_ms, 2),
                "total_requests": stats.total_requests,
            }
            for key, stats in sorted_endpoints
        ]

    @property
    def total_requests(self) -> int:
        return self._total_requests

    @property
    def total_errors(self) -> int:
        return self._total_errors


api_metrics = ApiMetricsCollector()


def _queue_name_from_broker_url() -> str:
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
