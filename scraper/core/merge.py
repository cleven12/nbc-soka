"""Merge scraped collections by stable id (for incremental sync)."""

from __future__ import annotations

from typing import Any


def merge_items_by_id(
    existing: list[Any],
    updates: list[Any],
    *,
    id_key: str = "id",
) -> list[dict[str, Any]]:
    """Upsert `updates` into `existing` by `id_key`.

    - Items in ``updates`` replace same-id rows from ``existing``.
    - Items only in ``existing`` are kept.
    - Non-dict rows and rows without an id are dropped from the result base;
      update rows without id are appended as-is (rare).
    - Result is sorted by numeric id when possible, else by string id.
    """
    by_id: dict[Any, dict[str, Any]] = {}

    for item in existing:
        if not isinstance(item, dict) or id_key not in item:
            continue
        by_id[item[id_key]] = item

    extras: list[dict[str, Any]] = []
    for item in updates:
        if not isinstance(item, dict):
            continue
        if id_key not in item:
            extras.append(item)
            continue
        by_id[item[id_key]] = item

    def _sort_key(row: dict[str, Any]) -> tuple[int, Any]:
        raw = row.get(id_key)
        try:
            return (0, int(raw))
        except (TypeError, ValueError):
            return (1, str(raw))

    merged = sorted(by_id.values(), key=_sort_key)
    merged.extend(extras)
    return merged


def load_artifact_items(payload: Any) -> list[Any]:
    """Extract ``items`` list from an Artifact-shaped dict or bare list."""
    if payload is None:
        return []
    if isinstance(payload, list):
        return list(payload)
    if isinstance(payload, dict):
        items = payload.get("items")
        if isinstance(items, list):
            return list(items)
    return []
