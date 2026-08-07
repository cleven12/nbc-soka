"""Shared envelope models for scraped artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class ArtifactMeta(BaseModel):
    source: str
    resource: str
    scraped_at: str = Field(default_factory=utc_now_iso)
    api_root: str | None = None
    count: int = 0
    filters: dict[str, Any] = Field(default_factory=dict)


class Artifact(BaseModel):
    source: str
    resource: str
    scraped_at: str = Field(default_factory=utc_now_iso)
    api_root: str | None = None
    count: int = 0
    filters: dict[str, Any] = Field(default_factory=dict)
    items: list[Any] = Field(default_factory=list)

    @classmethod
    def from_items(
        cls,
        *,
        source: str,
        resource: str,
        items: list[Any],
        api_root: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> Artifact:
        return cls(
            source=source,
            resource=resource,
            api_root=api_root,
            count=len(items),
            filters=filters or {},
            items=items,
        )
