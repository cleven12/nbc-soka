from pathlib import Path

from fastapi.testclient import TestClient

from api.app import create_app
from scraper.utils.jsonio import write_json


def _seed(tmp_path: Path) -> Path:
    source = tmp_path / "ligikuu"
    meta = tmp_path / "meta"
    source.mkdir()
    (source / "normalized").mkdir()
    (source / "seasons").mkdir()
    meta.mkdir()

    write_json(
        source / "index.json",
        {"source": "ligikuu", "scraped_at": "2026-07-24T00:00:00+00:00", "resources": {}},
    )
    write_json(
        source / "normalized" / "seasons.json",
        {
            "source": "ligikuu",
            "resource": "seasons",
            "scraped_at": "2026-07-24T00:00:00+00:00",
            "count": 1,
            "items": [{"id": 431, "slug": "2026-27", "name": "2026/27"}],
        },
    )
    write_json(
        source / "normalized" / "events.json",
        {
            "source": "ligikuu",
            "resource": "events",
            "scraped_at": "2026-07-24T00:00:00+00:00",
            "count": 1,
            "items": [
                {
                    "id": 1,
                    "name": "A vs B",
                    "seasons": [431],
                    "leagues": [432],
                    "status": "publish",
                    "home_score": 1,
                    "away_score": 0,
                }
            ],
        },
    )
    write_json(
        source / "normalized" / "tables.json",
        {
            "source": "ligikuu",
            "resource": "tables",
            "scraped_at": "2026-07-24T00:00:00+00:00",
            "count": 1,
            "items": [
                {
                    "id": 10,
                    "name": "NBC 2026/27",
                    "seasons": [431],
                    "leagues": [432],
                    "standings": [],
                }
            ],
        },
    )
    write_json(
        source / "normalized" / "teams.json",
        {
            "source": "ligikuu",
            "resource": "teams",
            "scraped_at": "2026-07-24T00:00:00+00:00",
            "count": 1,
            "items": [{"id": 1, "name": "Simba SC", "slug": "simba-sc"}],
        },
    )
    write_json(
        source / "seasons" / "2026-27.json",
        {
            "season": {"id": 431, "slug": "2026-27"},
            "events": [],
            "tables": [],
            "teams": [],
        },
    )
    write_json(meta / "last_run.json", {"ok": True, "scraped_at": "2026-07-24T00:00:00+00:00"})
    return tmp_path


def test_simple_paths_for_everyone(tmp_path: Path):
    client = TestClient(create_app(data_dir=_seed(tmp_path)))

    home = client.get("/")
    assert home.status_code == 200
    assert "NBC Ligi Kuu" in home.text
    assert "Kiswahili" in home.text

    health = client.get("/health").json()
    assert health["ok"] is True
    assert health["has_data"] is True

    scores = client.get("/scores", params={"season": "2026-27"}).json()
    assert scores["count"] == 1
    assert scores["items"][0]["home_score"] == 1

    table = client.get("/table", params={"season": "2026-27"}).json()
    assert table["count"] == 1

    teams = client.get("/teams").json()
    assert teams["count"] == 1

    season = client.get("/seasons/2026-27")
    assert season.status_code == 200


def test_api_v1_still_works(tmp_path: Path):
    client = TestClient(create_app(data_dir=_seed(tmp_path)))
    assert client.get("/api/v1/sources/ligikuu").status_code == 200
    events = client.get(
        "/api/v1/sources/ligikuu/events", params={"season_id": 431}
    ).json()
    assert events["count"] == 1
