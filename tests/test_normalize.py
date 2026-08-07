from scraper.models.sportspress import normalize_event, normalize_table, normalize_team


def test_normalize_event_scores():
    event = normalize_event(
        {
            "id": 16613,
            "title": {"rendered": "JKT Tanzania vs Young Africans"},
            "slug": "jkt-vs-yanga",
            "date": "2026-06-30T16:00:00",
            "status": "publish",
            "teams": [268, 292],
            "main_results": ["0", "3"],
            "outcome": {"268": "loss", "292": "win"},
            "leagues": [418],
            "seasons": [417],
            "venues": [],
            "winner": 292,
            "format": "league",
        }
    )
    assert event.home_team_id == 268
    assert event.away_team_id == 292
    assert event.home_score == 0
    assert event.away_score == 3
    assert event.is_placeholder is False


def test_normalize_placeholder_event():
    event = normalize_event(
        {
            "id": 1,
            "title": {"rendered": ""},
            "teams": [-1, -1],
            "main_results": [],
            "leagues": [],
            "seasons": [],
        }
    )
    assert event.is_placeholder is True
    assert event.home_team_id is None


def test_normalize_table_standings():
    table = normalize_table(
        {
            "id": 17188,
            "title": {"rendered": "NBC PREMIER LEAGUE 2026/2027"},
            "slug": "nbc-premier-league-2026-2027",
            "leagues": [432],
            "seasons": [431],
            "data": {
                "294": {
                    "name": "Azam",
                    "pos": 1,
                    "p": "2",
                    "w": "2",
                    "d": "0",
                    "l": "0",
                    "f": "4",
                    "a": "1",
                    "gd": "3",
                    "pts": "6",
                }
            },
        }
    )
    assert table.standings[0].team_id == 294
    assert table.standings[0].points == 6
    assert table.standings[0].name == "Azam"


def test_normalize_team():
    team = normalize_team(
        {
            "id": 14180,
            "title": {"rendered": "Bandari Tanzania"},
            "slug": "bandari-tanzania",
            "abbreviation": "BAN",
            "leagues": [421],
            "seasons": [417],
            "venues": [125],
            "status": "publish",
        }
    )
    assert team.name == "Bandari Tanzania"
    assert team.abbreviation == "BAN"
