"""Ligi Kuu (ligikuu.co.tz) SportsPress adapter."""

from __future__ import annotations

from typing import Any

from scraper.core.client import WPClient


class LigikuuAdapter:
    def __init__(
        self,
        *,
        base_url: str,
        user_agent: str,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        min_delay_ms: int = 250,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = WPClient(
            base_url=self.base_url,
            user_agent=user_agent,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            min_delay_ms=min_delay_ms,
        )

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> LigikuuAdapter:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch_collection(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        per_page: int = 100,
        max_pages: int | None = None,
    ) -> list[dict[str, Any]]:
        items = self.client.paginate(
            path,
            params=params,
            per_page=per_page,
            max_pages=max_pages,
        )
        return [item for item in items if isinstance(item, dict)]

    def fetch_one(self, path: str) -> dict[str, Any]:
        payload, _ = self.client.get_json(path)
        if not isinstance(payload, dict):
            raise TypeError(f"Expected object from {path}")
        return payload
