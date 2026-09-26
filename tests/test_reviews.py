"""Owner rulings on disk (``tff_catalog.reviews``): directories, file names and format."""

import json
import tomllib
from datetime import date

import pytest
from jsonschema import Draft202012Validator
from tests.helpers import ROOT

from tff_catalog import cli, reviews
from tff_catalog.paths import Paths

REVIEWS = ROOT / "data" / "reviews"
FILES = sorted(p for p in REVIEWS.rglob("*") if p.is_file() and p.name != ".gitkeep")
SCHEMA = json.loads((ROOT / "schemas" / reviews.SCHEMA).read_text(encoding="utf-8"))


def test_gate_dirs_are_distinct_and_used_by_the_cli() -> None:
    assert len(set(reviews.GATE_DIRS.values())) == len(reviews.GATE_DIRS)
    assert cli.GATES == reviews.GATES == tuple(reviews.GATE_DIRS)
    paths = Paths.for_root(ROOT)
    assert reviews.gate_dir(paths, "T") == REVIEWS / "terms"
    assert reviews.gate_dir(paths, "SITE") == REVIEWS / "site"


def test_the_rulings_of_2026_09_25_are_present() -> None:
    names = {p.relative_to(REVIEWS).as_posix() for p in FILES}
    assert {f"{d}/2026-09-25.toml" for d in ("terms", "method", "site")} <= names


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.relative_to(REVIEWS).as_posix())
def test_rulings_file_follows_the_format(path) -> None:
    assert path.parent.parent == REVIEWS, "rulings sit one directory deep"
    assert path.parent.name in reviews.GATE_DIRS.values(), path.parent.name
    assert path.suffix == ".toml"
    assert date.fromisoformat(path.stem).isoformat() == path.stem
    doc = tomllib.loads(path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(SCHEMA).iter_errors(doc), key=lambda e: e.json_path)
    assert [f"{e.json_path}: {e.message}" for e in errors] == []


def test_schema_rejects_a_ruling_without_its_reason() -> None:
    validator = Draft202012Validator(SCHEMA)
    assert not validator.is_valid({"M1": {"ruling": "x", "choice": "a", "recommended": True}})
    assert not validator.is_valid({"M1": {"ruling": "x", "reason": "y", "choice": "a"}})
    assert validator.is_valid(
        {"M1": {"ruling": "x", "reason": "y", "choice": "a", "recommended": True}}
    )


def test_ruling_m9_is_the_owners_choice_b() -> None:
    method = tomllib.loads((REVIEWS / "method" / "2026-09-25.toml").read_text(encoding="utf-8"))
    assert (method["M9"]["choice"], method["M9"]["recommended"]) == ("b", False)
    terms = tomllib.loads((REVIEWS / "terms" / "2026-09-25.toml").read_text(encoding="utf-8"))
    assert terms["T3"]["choice"] == "a"
