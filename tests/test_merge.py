from scraper.core.merge import load_artifact_items, merge_items_by_id
from scraper.core.pipeline import ScrapePipeline


def test_merge_items_by_id_upserts_and_keeps():
    existing = [
        {"id": 1, "name": "old-a", "score": 0},
        {"id": 2, "name": "keep-b", "score": 1},
    ]
    updates = [
        {"id": 1, "name": "new-a", "score": 2},
        {"id": 3, "name": "new-c", "score": 3},
    ]
    merged = merge_items_by_id(existing, updates)
    by_id = {row["id"]: row for row in merged}
    assert set(by_id) == {1, 2, 3}
    assert by_id[1]["name"] == "new-a"
    assert by_id[1]["score"] == 2
    assert by_id[2]["name"] == "keep-b"
    assert by_id[3]["name"] == "new-c"


def test_merge_sorts_by_numeric_id():
    merged = merge_items_by_id(
        [{"id": 10}, {"id": 2}],
        [{"id": 3}],
    )
    assert [row["id"] for row in merged] == [2, 3, 10]


def test_load_artifact_items():
    assert load_artifact_items({"items": [{"id": 1}]}) == [{"id": 1}]
    assert load_artifact_items([{"id": 2}]) == [{"id": 2}]
    assert load_artifact_items(None) == []
    assert load_artifact_items({"count": 0}) == []


def test_resolve_modified_after_none_without_corpus(tmp_path):
    pipe = ScrapePipeline(out_dir=tmp_path, incremental=True)
    assert pipe._resolve_modified_after({"ok": True, "scraped_at": "2026-08-01T12:00:00+00:00"}) is None


def test_resolve_modified_after_applies_overlap(tmp_path):
    raw = tmp_path / "ligikuu" / "raw"
    raw.mkdir(parents=True)
    (raw / "events.json").write_text('{"items":[{"id":1}]}', encoding="utf-8")
    pipe = ScrapePipeline(
        out_dir=tmp_path,
        incremental=True,
        modified_after_overlap_minutes=60,
    )
    ts = pipe._resolve_modified_after(
        {"ok": True, "scraped_at": "2026-08-01T12:00:00+00:00"}
    )
    assert ts == "2026-08-01T11:00:00+00:00"


def test_incremental_defaults_off_when_full():
    pipe = ScrapePipeline(full=True, incremental=True)
    assert pipe.incremental is False
    assert pipe.full is True
