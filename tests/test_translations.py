"""All translations have exactly the keys of strings.json."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

BASE = Path(__file__).parent.parent / "custom_components" / "msn_weather"


def _keys(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _keys(v, f"{prefix}{k}.")
    else:
        yield prefix.rstrip(".")


STRINGS = set(_keys(json.loads((BASE / "strings.json").read_text())))


@pytest.mark.parametrize("path", sorted((BASE / "translations").glob("*.json")), ids=lambda p: p.stem)
def test_translation_keys(path: Path) -> None:
    keys = set(_keys(json.loads(path.read_text())))
    assert keys == STRINGS, {"missing": sorted(STRINGS - keys), "extra": sorted(keys - STRINGS)}
