"""End-to-end scrape pipeline for a configured source."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from rich.console import Console

from scraper.adapters.ligikuu import LigikuuAdapter
from scraper.core.config import enabled_resources, http_settings, load_source_config, output_dir
from scraper.core.merge import load_artifact_items, merge_items_by_id
from scraper.core.season import SeasonPlan, build_season_plan, filter_items_by_season_or_league
from scraper.core.storage import DataStore
from scraper.models.common import Artifact, utc_now_iso
from scraper.models.sportspress import (
    normalize_event,
    normalize_table,
    normalize_taxonomy,
    normalize_team,
)
from scraper.utils.jsonio import read_json

console = Console(stderr=True)

# Post-like SportsPress resources that support modified_after and merge-by-id.
INCREMENTAL_RESOURCES = frozenset(
    {"events", "tables", "teams", "calendars", "lists", "players"}
)
# Always re-fetch completely (small taxonomies / structural).
FULL_ALWAYS_RESOURCES = frozenset({"seasons", "leagues", "venues"})


class ScrapePipeline:
    def __init__(
        self,
        *,
        config_path: Path | str | None = None,
        out_dir: Path | str | None = None,
        full: bool = False,
        incremental: bool | None = None,
        keep_recent_seasons: int = 3,
        include_players: bool = False,
        max_pages: int | None = None,
        modified_after_overlap_minutes: int = 60,
    ) -> None:
        self.config = load_source_config(config_path)
        self.source_id = str(self.config.get("id") or "ligikuu")
        self.full = full
        # Default: incremental when not --full (uses last_run if present).
        if incremental is None:
            self.incremental = not full
        else:
            self.incremental = incremental and not full
        self.keep_recent_seasons = keep_recent_seasons
        self.include_players = include_players
        self.max_pages = max_pages
        self.modified_after_overlap_minutes = modified_after_overlap_minutes
        self.store = DataStore(output_dir(self.config, out_dir), source_id=self.source_id)
        self.http = http_settings(self.config)

    def run(self) -> dict[str, Any]:
        self.store.ensure_layout()
        scraped_at = utc_now_iso()
        sp = self.config["sportspress"]
        base_url = sp["base_url"]
        default_query = dict(sp.get("default_query") or {})
        per_page = int(default_query.get("per_page") or 100)
        inc_cfg = dict(sp.get("incremental") or {})
        modified_param = str(inc_cfg.get("modified_after_param") or "modified_after")

        last_run = self.store.read_last_run()
        modified_after = self._resolve_modified_after(last_run) if self.incremental else None
        use_incremental = bool(self.incremental and modified_after)

        resources = enabled_resources(self.config)
        if self.include_players:
            for r in self.config.get("sportspress", {}).get("resources") or []:
                if r.get("name") == "players":
                    r = dict(r)
                    r["enabled"] = True
                    resources.append(r)
            resources = sorted(resources, key=lambda r: int(r.get("priority") or 99))

        summary: dict[str, Any] = {
            "source": self.source_id,
            "scraped_at": scraped_at,
            "api_root": base_url,
            "resources": {},
            "season_plan": {},
            "paths": [],
            "mode": "incremental" if use_incremental else ("full" if self.full else "refresh"),
            "modified_after": modified_after,
        }

        if use_incremental:
            console.print(
                f"[bold]Incremental mode[/bold] — {modified_param}={modified_after}"
            )
        elif self.full:
            console.print("[bold]Full mode[/bold] — no season filter, full collections")
        else:
            console.print(
                "[bold]Refresh mode[/bold] — full collections, season-filtered store "
                "(no prior last_run or incremental disabled)"
            )

        with LigikuuAdapter(
            base_url=base_url,
            user_agent=str(self.http.get("user_agent") or "nbc-soka/0.1"),
            timeout_seconds=float(self.http.get("timeout_seconds") or 30),
            max_retries=int(self.http.get("max_retries") or 3),
            min_delay_ms=int(self.http.get("min_delay_between_requests_ms") or 250),
        ) as adapter:
            # 1) Always pull taxonomies first for season auto-detection.
            console.print("[bold]Fetching seasons & leagues for auto-tracking…[/bold]")
            seasons_raw = adapter.fetch_collection(
                "/seasons", params={}, per_page=per_page, max_pages=self.max_pages
            )
            leagues_raw = adapter.fetch_collection(
                "/leagues", params={}, per_page=per_page, max_pages=self.max_pages
            )

            plan = build_season_plan(
                seasons=seasons_raw,
                leagues=leagues_raw,
                keep_recent_seasons=self.keep_recent_seasons,
                config_focus=self.config.get("focus") or {},
            )
            summary["season_plan"] = plan.to_dict()
            console.print(
                f"Active season ids: {plan.active_season_ids} | "
                f"tracked competitions: {len(plan.competitions)}"
            )

            # Persist taxonomies
            for resource_name, raw_items, normalizer in (
                ("seasons", seasons_raw, normalize_taxonomy),
                ("leagues", leagues_raw, normalize_taxonomy),
            ):
                paths = self._persist_resource(
                    resource_name=resource_name,
                    raw_items=raw_items,
                    api_root=base_url,
                    normalizer=normalizer,
                    filters={},
                )
                summary["resources"][resource_name] = {
                    "raw_count": len(raw_items),
                    "paths": [str(p) for p in paths],
                }
                summary["paths"].extend(str(p) for p in paths)

            season_ids = set(plan.active_season_ids)
            league_ids = set(plan.active_league_ids)

            # 2) Remaining enabled resources
            skip = {"seasons", "leagues"}
            for resource in resources:
                name = resource["name"]
                if name in skip:
                    continue
                path = resource["path"]
                params = dict(default_query)
                params.update(resource.get("default_query") or {})
                # Remove page from sticky defaults; client paginates.
                params.pop("page", None)

                can_incremental = (
                    use_incremental
                    and name in INCREMENTAL_RESOURCES
                    and name not in FULL_ALWAYS_RESOURCES
                )
                if can_incremental and modified_after:
                    params[modified_param] = modified_after

                mode_label = "delta" if can_incremental else "full"
                console.print(f"[cyan]Fetching {name}[/cyan] ({mode_label})…")
                fetched = adapter.fetch_collection(
                    path,
                    params=params,
                    per_page=per_page,
                    max_pages=self.max_pages,
                )

                fetched_count = len(fetched)
                if can_incremental:
                    existing = self._load_existing_items(name)
                    raw_items = merge_items_by_id(existing, fetched)
                    console.print(
                        f"  merged {name}: existing={len(existing)} "
                        f"delta={fetched_count} → total={len(raw_items)}"
                    )
                else:
                    raw_items = fetched

                if not self.full and name in {"events", "tables", "calendars", "lists", "teams"}:
                    filtered = filter_items_by_season_or_league(
                        raw_items,
                        season_ids=season_ids,
                        league_ids=league_ids,
                    )
                    # Teams: if filter empties (missing taxonomy on some teams), keep all.
                    if name == "teams" and not filtered:
                        filtered = raw_items
                    raw_for_norm = filtered
                else:
                    raw_for_norm = raw_items

                normalizer = {
                    "teams": normalize_team,
                    "tables": normalize_table,
                    "events": normalize_event,
                    "venues": normalize_taxonomy,
                }.get(name)

                paths = self._persist_resource(
                    resource_name=name,
                    raw_items=raw_for_norm if name != "venues" else raw_items,
                    api_root=base_url,
                    normalizer=normalizer,
                    filters={
                        "active_season_ids": sorted(season_ids),
                        "active_league_ids": sorted(league_ids),
                        "full": self.full,
                        "incremental": can_incremental,
                        "modified_after": modified_after if can_incremental else None,
                        "delta_count": fetched_count if can_incremental else None,
                    },
                    also_store_all_raw=raw_items if name in {"events", "tables"} else None,
                )
                summary["resources"][name] = {
                    "raw_count": len(raw_items),
                    "fetched_count": fetched_count,
                    "stored_count": len(raw_for_norm if name != "venues" else raw_items),
                    "incremental": can_incremental,
                    "paths": [str(p) for p in paths],
                }
                summary["paths"].extend(str(p) for p in paths)

            # 3) Season bundles (API-friendly slices)
            self._write_season_bundles(plan, scraped_at=scraped_at, api_root=base_url)

        index = {
            "source": self.source_id,
            "scraped_at": scraped_at,
            "api_root": base_url,
            "mode": summary["mode"],
            "modified_after": modified_after,
            "season_plan": plan.to_dict(),
            "resources": {
                name: info.get("stored_count", info.get("raw_count"))
                for name, info in summary["resources"].items()
            },
            "endpoints_hint": {
                "list_resources": "/api/v1/sources/ligikuu",
                "events": "/api/v1/sources/ligikuu/events",
                "tables": "/api/v1/sources/ligikuu/tables",
                "seasons": "/api/v1/sources/ligikuu/seasons",
                "season_bundle": "/api/v1/sources/ligikuu/seasons/{slug}",
            },
        }
        index_path = self.store.write_index(index)
        last_run_path = self.store.write_last_run(
            {
                "ok": True,
                "scraped_at": scraped_at,
                "source": self.source_id,
                "mode": summary["mode"],
                "modified_after_used": modified_after,
                "season_plan": plan.to_dict(),
                "resource_counts": {
                    k: v.get("stored_count", v.get("raw_count"))
                    for k, v in summary["resources"].items()
                },
            }
        )
        summary["paths"].extend([str(index_path), str(last_run_path)])
        summary["ok"] = True
        console.print(f"[green]Done.[/green] index → {index_path} (mode={summary['mode']})")
        return summary

    def _resolve_modified_after(self, last_run: dict[str, Any] | None) -> str | None:
        """Return ISO timestamp for modified_after, or None if incremental cannot run."""
        if not last_run or not last_run.get("ok"):
            return None
        # Prefer previous scraped_at; require existing event store so merge is meaningful.
        if not self._has_existing_corpus():
            return None
        raw_ts = last_run.get("scraped_at")
        if not raw_ts or not isinstance(raw_ts, str):
            return None
        try:
            ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        except ValueError:
            return None
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        # Overlap window so edge edits near the last run boundary are not missed.
        ts = ts - timedelta(minutes=max(0, self.modified_after_overlap_minutes))
        return ts.replace(microsecond=0).isoformat()

    def _has_existing_corpus(self) -> bool:
        """True if we already have event (or table) data to merge into."""
        for name in ("events_all.json", "events.json", "tables_all.json", "tables.json"):
            path = self.store.source_dir / "raw" / name
            if path.is_file():
                return True
            if (self.store.source_dir / name).is_file():
                return True
        return False

    def _load_existing_items(self, resource_name: str) -> list[Any]:
        """Load previously stored items for merge (prefer unfiltered *_all dumps)."""
        candidates = [
            self.store.source_dir / "raw" / f"{resource_name}_all.json",
            self.store.source_dir / "raw" / f"{resource_name}.json",
            self.store.source_dir / f"{resource_name}.json",
        ]
        for path in candidates:
            if not path.is_file():
                continue
            try:
                payload = read_json(path)
            except Exception:
                continue
            items = load_artifact_items(payload)
            if items:
                return items
        return []


    def _persist_resource(
        self,
        *,
        resource_name: str,
        raw_items: list[Any],
        api_root: str,
        normalizer: Any | None,
        filters: dict[str, Any],
        also_store_all_raw: list[Any] | None = None,
    ) -> list[Path]:
        paths: list[Path] = []
        raw_artifact = Artifact.from_items(
            source=self.source_id,
            resource=resource_name,
            items=raw_items,
            api_root=api_root,
            filters=filters,
        )
        paths.append(self.store.write_artifact(raw_artifact, f"{resource_name}.json"))
        paths.append(
            self.store.write_raw(
                f"{resource_name}.json",
                raw_artifact.model_dump(mode="json"),
            )
        )

        if also_store_all_raw is not None and also_store_all_raw is not raw_items:
            full_art = Artifact.from_items(
                source=self.source_id,
                resource=f"{resource_name}_all",
                items=also_store_all_raw,
                api_root=api_root,
                filters={"full_dump": True},
            )
            paths.append(self.store.write_raw(f"{resource_name}_all.json", full_art.model_dump(mode="json")))

        if normalizer is not None:
            normalized_items: list[Any] = []
            for item in raw_items:
                if not isinstance(item, dict):
                    continue
                normalized_items.append(normalizer(item).model_dump(mode="json"))
            norm_artifact = Artifact.from_items(
                source=self.source_id,
                resource=resource_name,
                items=normalized_items,
                api_root=api_root,
                filters=filters,
            )
            paths.append(
                self.store.write_normalized(
                    f"{resource_name}.json",
                    norm_artifact.model_dump(mode="json"),
                )
            )
        return paths

    def _write_season_bundles(
        self,
        plan: SeasonPlan,
        *,
        scraped_at: str,
        api_root: str,
    ) -> None:
        """Write per-season JSON files for easy API / consumer access."""
        from scraper.utils.jsonio import read_json

        def _load_norm(name: str) -> list[dict[str, Any]]:
            path = self.store.source_dir / "normalized" / f"{name}.json"
            if not path.is_file():
                path = self.store.source_dir / f"{name}.json"
            if not path.is_file():
                return []
            data = read_json(path)
            items = data.get("items") if isinstance(data, dict) else data
            return list(items or [])

        events = _load_norm("events")
        tables = _load_norm("tables")
        teams = _load_norm("teams")

        # Map season id → slug
        season_meta = {int(s["id"]): s for s in plan.seasons if "id" in s}

        for season_id in plan.active_season_ids:
            meta = season_meta.get(season_id) or {"id": season_id, "slug": str(season_id)}
            slug = str(meta.get("slug") or season_id)
            season_events = [e for e in events if season_id in (e.get("seasons") or [])]
            season_tables = [t for t in tables if season_id in (t.get("seasons") or [])]
            # teams often list seasons
            season_teams = [t for t in teams if season_id in (t.get("seasons") or [])]
            comps = [
                c
                for c in plan.competitions
                if any(
                    tok in f"{c.slug} {c.name}"
                    for tok in (
                        slug,
                        slug.replace("-", "/"),
                        slug.replace("-", ""),
                    )
                )
                or True  # include all tracked comps; filter tighter below
            ]
            # Tighter: competitions whose slug contains season years
            year_bits = slug.replace("/", "-").split("-")
            comps = [
                {
                    "id": c.id,
                    "slug": c.slug,
                    "name": c.name,
                    "kind": c.kind,
                }
                for c in plan.competitions
                if any(bit in c.slug for bit in year_bits if len(bit) >= 2)
                or any(bit in c.name for bit in year_bits if len(bit) >= 2)
            ]

            bundle = {
                "source": self.source_id,
                "scraped_at": scraped_at,
                "api_root": api_root,
                "season": meta,
                "competitions": comps,
                "counts": {
                    "events": len(season_events),
                    "tables": len(season_tables),
                    "teams": len(season_teams),
                },
                "events": season_events,
                "tables": season_tables,
                "teams": season_teams,
            }
            path = self.store.write_season_bundle(slug, bundle)
            console.print(f"  season bundle [bold]{slug}[/bold] → {path} ({len(season_events)} events)")
