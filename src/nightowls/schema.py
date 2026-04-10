from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any


@lru_cache(maxsize=1)
def load_schema() -> dict[str, Any]:
    schema_path = files("nightowls").joinpath("schemas/nightowls.schema.json")
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
