"""Every JSON Schema under schemas/ (BRIEF item 4): 2020-12, valid, no ``format``, unique ``$id``."""

import json

import pytest
from jsonschema import Draft202012Validator
from tests.helpers import ROOT

SCHEMAS = sorted((ROOT / "schemas").rglob("*.schema.json"))


def _uses_format(node: object) -> bool:
    if isinstance(node, dict):
        if isinstance(node.get("format"), str):
            return True
        return any(_uses_format(v) for k, v in node.items() if k != "properties") or any(
            _uses_format(v) for v in node.get("properties", {}).values()
        )
    if isinstance(node, list):
        return any(_uses_format(v) for v in node)
    return False


@pytest.mark.parametrize("path", SCHEMAS, ids=lambda p: p.relative_to(ROOT / "schemas").as_posix())
def test_schema_is_valid_2020_12(path) -> None:
    schema = json.loads(path.read_text(encoding="utf-8"))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)
    assert not _uses_format(schema), "use pattern ^https:// instead of format"


def test_schema_ids_are_unique() -> None:
    ids = [json.loads(p.read_text(encoding="utf-8"))["$id"] for p in SCHEMAS]
    assert len(ids) == len(set(ids))
