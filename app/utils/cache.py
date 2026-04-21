"""
Simple in-memory response cache for FastAPI GET endpoints.

This cache is process-local and is cleared on write operations. It is safe for
single-process deployments and provides a small performance boost for repeated
reads between writes.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import time


@dataclass
class CacheEntry:
    body: bytes
    status_code: int
    media_type: str | None
    headers: dict[str, str]
    expires_at: float


class InMemoryCache:
    def __init__(self, ttl_seconds: int = 60):
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, CacheEntry] = {}
        self._lock = Lock()

    def get(self, key: str) -> CacheEntry | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.expires_at <= time():
                self._store.pop(key, None)
                return None
            return entry

    def set(
        self,
        key: str,
        *,
        body: bytes,
        status_code: int,
        media_type: str | None,
        headers: dict[str, str],
    ) -> None:
        with self._lock:
            self._store[key] = CacheEntry(
                body=body,
                status_code=status_code,
                media_type=media_type,
                headers=headers,
                expires_at=time() + self.ttl_seconds,
            )

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


response_cache = InMemoryCache(ttl_seconds=60)
