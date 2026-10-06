"""Persistencia simple y explícita de resultados experimentales."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def save_results(path: str | Path, results: Any, **metadata) -> None:
    payload = {
        "metadata": {"created_at": datetime.now(UTC).isoformat(), **metadata},
        "results": results,
    }
    with Path(path).open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=True, indent=2, default=list)


def load_results(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)
