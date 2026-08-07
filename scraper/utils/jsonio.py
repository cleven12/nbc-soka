"""JSON read/write helpers (orjson when available)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import orjson
except ImportError:  # pragma: no cover
    orjson = None  # type: ignore[assignment]


def loads(data: bytes | str) -> Any:
    if orjson is not None:
        if isinstance(data, str):
            data = data.encode("utf-8")
        return orjson.loads(data)
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    return json.loads(data)


def dumps(obj: Any, *, pretty: bool = True) -> bytes:
    if orjson is not None:
        option = orjson.OPT_SORT_KEYS
        if pretty:
            option |= orjson.OPT_INDENT_2
        return orjson.dumps(obj, option=option)
    text = json.dumps(obj, indent=2 if pretty else None, sort_keys=True, ensure_ascii=False)
    return (text + ("\n" if pretty else "")).encode("utf-8")


def read_json(path: Path) -> Any:
    return loads(path.read_bytes())


def write_json(path: Path, obj: Any, *, pretty: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(dumps(obj, pretty=pretty))
