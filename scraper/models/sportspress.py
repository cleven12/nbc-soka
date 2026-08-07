"""Normalized SportsPress entities used by the pipeline and API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


def _rendered_title(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return str(value.get("rendered") or "").strip()
    return str(value).strip()


class TaxonomyTerm(BaseModel):
    id: int
    name: str = ""
    slug: str = ""
    parent: int = 0
    count: int = 0
    description: str = ""


class Team(BaseModel):
    id: int
    name: str = ""
    slug: str = ""
    abbreviation: str | None = None
    leagues: list[int] = Field(default_factory=list)
    seasons: list[int] = Field(default_factory=list)
    venues: list[int] = Field(default_factory=list)
    url: str | None = None
    status: str | None = None


class StandingRow(BaseModel):
    team_id: int
    name: str = ""
    pos: int | None = None
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goal_diff: int = 0
    points: int = 0
    raw: dict[str, Any] = Field(default_factory=dict)


class LeagueTable(BaseModel):
    id: int
    name: str = ""
    slug: str = ""
    leagues: list[int] = Field(default_factory=list)
    seasons: list[int] = Field(default_factory=list)
    status: str | None = None
    standings: list[StandingRow] = Field(default_factory=list)


class Event(BaseModel):
    id: int
    name: str = ""
    slug: str = ""
    date: str | None = None
    date_gmt: str | None = None
    status: str | None = None
    home_team_id: int | None = None
    away_team_id: int | None = None
    home_score: int | None = None
    away_score: int | None = None
    outcome: dict[str, str] = Field(default_factory=dict)
    winner_id: int | None = None
    leagues: list[int] = Field(default_factory=list)
    seasons: list[int] = Field(default_factory=list)
    venues: list[int] = Field(default_factory=list)
    format: str | None = None
    day: Any = None
    minutes: Any = None
    is_placeholder: bool = False
    raw_teams: list[int] = Field(default_factory=list)
    raw_main_results: list[Any] = Field(default_factory=list)

    @field_validator("home_score", "away_score", "winner_id", mode="before")
    @classmethod
    def _empty_to_none(cls, value: Any) -> Any:
        if value is None or value == "" or value == []:
            return None
        return value


def parse_intish(value: Any) -> int | None:
    if value is None or value == "" or value is False:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_taxonomy(item: dict[str, Any]) -> TaxonomyTerm:
    return TaxonomyTerm(
        id=int(item["id"]),
        name=str(item.get("name") or ""),
        slug=str(item.get("slug") or ""),
        parent=int(item.get("parent") or 0),
        count=int(item.get("count") or 0),
        description=str(item.get("description") or ""),
    )


def normalize_team(item: dict[str, Any]) -> Team:
    return Team(
        id=int(item["id"]),
        name=_rendered_title(item.get("title")),
        slug=str(item.get("slug") or ""),
        abbreviation=item.get("abbreviation") or None,
        leagues=[int(x) for x in (item.get("leagues") or [])],
        seasons=[int(x) for x in (item.get("seasons") or [])],
        venues=[int(x) for x in (item.get("venues") or [])],
        url=item.get("url") or None,
        status=item.get("status"),
    )


def normalize_table(item: dict[str, Any]) -> LeagueTable:
    standings: list[StandingRow] = []
    data = item.get("data") or {}
    if isinstance(data, dict):
        for team_key, row in data.items():
            if not isinstance(row, dict):
                continue
            team_id = parse_intish(team_key)
            if team_id is None:
                continue
            standings.append(
                StandingRow(
                    team_id=team_id,
                    name=str(row.get("name") or ""),
                    pos=parse_intish(row.get("pos")),
                    played=parse_intish(row.get("p")) or 0,
                    won=parse_intish(row.get("w")) or 0,
                    drawn=parse_intish(row.get("d")) or 0,
                    lost=parse_intish(row.get("l")) or 0,
                    goals_for=parse_intish(row.get("f")) or 0,
                    goals_against=parse_intish(row.get("a")) or 0,
                    goal_diff=parse_intish(row.get("gd")) or 0,
                    points=parse_intish(row.get("pts")) or 0,
                    raw=row,
                )
            )
        standings.sort(key=lambda r: (r.pos is None, r.pos or 0, r.team_id))

    return LeagueTable(
        id=int(item["id"]),
        name=_rendered_title(item.get("title")),
        slug=str(item.get("slug") or ""),
        leagues=[int(x) for x in (item.get("leagues") or [])],
        seasons=[int(x) for x in (item.get("seasons") or [])],
        status=item.get("status"),
        standings=standings,
    )


def normalize_event(item: dict[str, Any]) -> Event:
    teams = [parse_intish(t) for t in (item.get("teams") or [])]
    teams_clean = [t for t in teams if t is not None]
    main = list(item.get("main_results") or [])

    home_id = teams_clean[0] if len(teams_clean) > 0 else None
    away_id = teams_clean[1] if len(teams_clean) > 1 else None
    home_score = parse_intish(main[0]) if len(main) > 0 else None
    away_score = parse_intish(main[1]) if len(main) > 1 else None

    winner_raw = item.get("winner")
    winner_id = parse_intish(winner_raw)
    if winner_id is None and isinstance(winner_raw, list) and winner_raw:
        winner_id = parse_intish(winner_raw[0])

    outcome: dict[str, str] = {}
    raw_outcome = item.get("outcome") or {}
    if isinstance(raw_outcome, dict):
        outcome = {str(k): str(v) for k, v in raw_outcome.items()}

    is_placeholder = (
        not teams_clean
        or any(t is not None and t < 0 for t in teams)
        or (home_id == -1 or away_id == -1)
    )

    return Event(
        id=int(item["id"]),
        name=_rendered_title(item.get("title")),
        slug=str(item.get("slug") or ""),
        date=item.get("date"),
        date_gmt=item.get("date_gmt"),
        status=item.get("status"),
        home_team_id=None if home_id is not None and home_id < 0 else home_id,
        away_team_id=None if away_id is not None and away_id < 0 else away_id,
        home_score=home_score,
        away_score=away_score,
        outcome=outcome,
        winner_id=winner_id,
        leagues=[int(x) for x in (item.get("leagues") or [])],
        seasons=[int(x) for x in (item.get("seasons") or [])],
        venues=[int(x) for x in (item.get("venues") or [])],
        format=item.get("format"),
        day=item.get("day"),
        minutes=item.get("minutes"),
        is_placeholder=bool(is_placeholder),
        raw_teams=[int(t) for t in teams_clean],
        raw_main_results=main,
    )
