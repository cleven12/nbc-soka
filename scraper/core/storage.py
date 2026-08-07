"""Write scraped artifacts to the data directory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scraper.models.common import Artifact, utc_now_iso
from scraper.utils.jsonio import read_json, write_json


class DataStore:
    def __init__(self, root: Path, *, source_id: str = "ligikuu", pretty: bool = True) -> None:
        self.root = Path(root)
        self.source_id = source_id
        self.pretty = pretty
        self.source_dir = self.root if self.root.name == source_id else self.root / source_id
        self.meta_dir = self.root / "meta" if self.root.name != source_id else self.root.parent / "meta"
        # Prefer data/meta + data/ligikuu layout
        if self.root.name == source_id:
            self.base = self.root.parent
            self.source_dir = self.root
            self.meta_dir = self.base / "meta"
        else:
            self.base = self.root
            self.source_dir = self.root / source_id
            self.meta_dir = self.root / "meta"

    def write_artifact(self, artifact: Artifact, filename: str) -> Path:
        path = self.source_dir / filename
        write_json(path, artifact.model_dump(mode="json"), pretty=self.pretty)
        return path

    def write_raw(self, name: str, payload: Any) -> Path:
        path = self.source_dir / "raw" / name
        write_json(path, payload, pretty=self.pretty)
        return path

    def write_normalized(self, name: str, payload: Any) -> Path:
        path = self.source_dir / "normalized" / name
        write_json(path, payload, pretty=self.pretty)
        return path

    def write_season_bundle(self, season_slug: str, payload: dict[str, Any]) -> Path:
        path = self.source_dir / "seasons" / f"{season_slug}.json"
        write_json(path, payload, pretty=self.pretty)
        return path

    def write_last_run(self, payload: dict[str, Any]) -> Path:
        path = self.meta_dir / "last_run.json"
        write_json(path, payload, pretty=self.pretty)
        return path

    def write_index(self, payload: dict[str, Any]) -> Path:
        path = self.source_dir / "index.json"
        write_json(path, payload, pretty=self.pretty)
        return path

    def read_last_run(self) -> dict[str, Any] | None:
        path = self.meta_dir / "last_run.json"
        if not path.is_file():
            return None
        data = read_json(path)
        return data if isinstance(data, dict) else None

    def ensure_layout(self) -> None:
        for path in (
            self.source_dir,
            self.source_dir / "raw",
            self.source_dir / "normalized",
            self.source_dir / "seasons",
            self.meta_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def touch_scraped_at(self) -> str:
        return utc_now_iso()
