"""Detect active / upcoming NBC seasons so new campaigns are stored automatically.

Ligi Kuu creates a **new league taxonomy id per season** (e.g. NBC PL 2025/26 = 418,
NBC PL 2026/27 = 432). The scraper must not hard-code a single league id forever.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Matches NBC Premier League style slugs across seasons.
NBC_PREMIER_SLUG = re.compile(
    r"^nbc[-_]?premier[-_]?league",
    re.IGNORECASE,
)
NBC_CHAMPIONSHIP_SLUG = re.compile(
    r"^nbc[-_]?championship",
    re.IGNORECASE,
)
SEASON_IN_SLUG = re.compile(
    r"(20\d{2})[-_/]?(20\d{2}|\d{2})",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CompetitionRef:
    id: int
    slug: str
    name: str
    season_ids: list[int] = field(default_factory=list)
    kind: str = "other"  # nbc_premier | nbc_championship | first_league | other


@dataclass
class SeasonPlan:
    """What the runner should track this run."""

    seasons: list[dict[str, Any]]
    competitions: list[CompetitionRef]
    active_season_ids: list[int]
    active_league_ids: list[int]
    focus_labels: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "seasons": self.seasons,
            "competitions": [
                {
                    "id": c.id,
                    "slug": c.slug,
                    "name": c.name,
                    "season_ids": c.season_ids,
                    "kind": c.kind,
                }
                for c in self.competitions
            ],
            "active_season_ids": self.active_season_ids,
            "active_league_ids": self.active_league_ids,
            "focus_labels": self.focus_labels,
        }


def _season_sort_key(item: dict[str, Any]) -> tuple[int, str]:
    slug = str(item.get("slug") or "")
    match = SEASON_IN_SLUG.search(slug) or SEASON_IN_SLUG.search(str(item.get("name") or ""))
    if match:
        start = int(match.group(1))
        return (start, slug)
    return (0, slug)


def classify_league(slug: str, name: str = "") -> str:
    text = f"{slug} {name}".lower()
    if NBC_PREMIER_SLUG.search(slug) or "nbc premier" in text:
        return "nbc_premier"
    if NBC_CHAMPIONSHIP_SLUG.search(slug) or "championship" in text and "nbc" in text:
        return "nbc_championship"
    if "first-league" in slug or "first league" in text:
        return "first_league"
    return "other"


def build_season_plan(
    *,
    seasons: list[dict[str, Any]],
    leagues: list[dict[str, Any]],
    keep_recent_seasons: int = 3,
    include_kinds: frozenset[str] | None = None,
    config_focus: dict[str, Any] | None = None,
) -> SeasonPlan:
    """Pick seasons + competitions to scrape.

    Always includes the newest seasons (so **2026/27 is picked up as soon as it
    exists on the API**) plus any kinds requested (default: NBC Premier + Championship).
    """
    kinds = include_kinds or frozenset({"nbc_premier", "nbc_championship"})
    focus = config_focus or {}

    sorted_seasons = sorted(seasons, key=_season_sort_key, reverse=True)
    recent = sorted_seasons[: max(1, keep_recent_seasons)]
    active_season_ids = [int(s["id"]) for s in recent if "id" in s]

    # Ensure config-known upcoming season ids are never dropped (e.g. 2026-27).
    for s in focus.get("seasons") or []:
        sid = int(s["id"])
        if sid not in active_season_ids:
            # Keep configured top seasons that look current/upcoming.
            slug = str(s.get("slug") or "")
            if any(x in slug for x in ("2025-26", "2026-27", "2027-28")):
                active_season_ids.append(sid)

    competitions: list[CompetitionRef] = []
    for league in leagues:
        slug = str(league.get("slug") or "")
        name = str(league.get("name") or "")
        kind = classify_league(slug, name)
        if kind not in kinds:
            continue
        competitions.append(
            CompetitionRef(
                id=int(league["id"]),
                slug=slug,
                name=name,
                season_ids=[],  # filled by relation when available
                kind=kind,
            )
        )

    # Prefer competitions whose slug mentions an active season year.
    active_year_tokens: set[str] = set()
    for s in seasons:
        if int(s.get("id", -1)) in active_season_ids:
            slug = str(s.get("slug") or "")
            name = str(s.get("name") or "")
            for match in SEASON_IN_SLUG.finditer(f"{slug} {name}"):
                active_year_tokens.add(match.group(1))
                active_year_tokens.add(match.group(0).replace("/", "-"))

    def _touches_active(comp: CompetitionRef) -> bool:
        blob = f"{comp.slug} {comp.name}"
        if not active_year_tokens:
            return True
        return any(token in blob for token in active_year_tokens) or any(
            y in blob for y in ("2025", "2026", "2027")
        )

    # Keep all NBC premier/championship; rank active ones first for labels.
    active_competitions = [c for c in competitions if _touches_active(c)]
    if not active_competitions:
        active_competitions = competitions

    active_league_ids = sorted({c.id for c in active_competitions})

    labels = [
        f"{c.kind}:{c.slug}"
        for c in sorted(active_competitions, key=lambda x: (x.kind, x.slug))
    ]

    return SeasonPlan(
        seasons=[
            {
                "id": int(s["id"]),
                "slug": s.get("slug"),
                "name": s.get("name"),
            }
            for s in sorted_seasons
        ],
        competitions=competitions,
        active_season_ids=sorted(set(active_season_ids)),
        active_league_ids=active_league_ids,
        focus_labels=labels,
    )


def filter_items_by_season_or_league(
    items: list[dict[str, Any]],
    *,
    season_ids: set[int] | None = None,
    league_ids: set[int] | None = None,
) -> list[dict[str, Any]]:
    """Keep items that touch any active season or league id."""
    if not season_ids and not league_ids:
        return items
    out: list[dict[str, Any]] = []
    for item in items:
        item_seasons = {int(x) for x in (item.get("seasons") or []) if x is not None}
        item_leagues = {int(x) for x in (item.get("leagues") or []) if x is not None}
        if season_ids and item_seasons & season_ids:
            out.append(item)
            continue
        if league_ids and item_leagues & league_ids:
            out.append(item)
            continue
        # Taxonomies themselves (seasons/leagues lists) have no seasons field — keep all.
        if "seasons" not in item and "leagues" not in item:
            out.append(item)
    return out
