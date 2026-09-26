"""Stage files (``tff_catalog.stageio``): every row type in ``STAGE_FILES`` round-trips."""

import collections.abc
import dataclasses
import json
import types
import typing
from datetime import date
from pathlib import Path
from typing import Any, Literal

import pytest
from jsonschema import Draft202012Validator
from tests.helpers import ROOT

from tff_catalog import stageio
from tff_catalog.corrections import Term
from tff_catalog.mapping import IndexEntry, entries_of, index_of
from tff_catalog.paths import Paths
from tff_catalog.records import RECORD_TYPES, Observation, SourceKey, attrs
from tff_catalog.stages import names as stage_names


def example(tp: Any, seed: int = 0) -> Any:
    """A deterministic value of type ``tp``, non-empty wherever it can be."""
    if isinstance(tp, typing.TypeAliasType):
        tp = tp.__value__
    origin, args = typing.get_origin(tp), typing.get_args(tp)
    if origin is Literal:
        return args[seed % len(args)]
    if origin in (typing.Union, types.UnionType):
        options = [a for a in args if a is not type(None)]
        return example(options[seed % len(options)], seed)
    if tp is Observation or tp in RECORD_TYPES.values():
        return Observation(
            source="synth",
            series="365d",
            key=SourceKey("brew-cask", f"font-x{seed}"),
            value=12.0 + seed,
            unit="installs",
            start=date(2025, 10, 1),
            end=date(2026, 9, 30),
            attrs=attrs(first_seen="2025-05-15", tap="homebrew/cask"),
        )
    if dataclasses.is_dataclass(tp):
        hints = typing.get_type_hints(tp)
        return tp(
            **{
                f.name: example(hints[f.name], seed + i)
                for i, f in enumerate(dataclasses.fields(tp))
            }
        )
    if origin is tuple:
        if len(args) == 2 and args[1] is Ellipsis:
            return (example(args[0], seed), example(args[0], seed + 1))
        return tuple(example(a, seed + i) for i, a in enumerate(args))
    if origin in (dict,) or (origin is not None and issubclass(origin, collections.abc.Mapping)):
        return {f"k{seed}": example(args[1], seed), f"k{seed + 1}": example(args[1], seed + 1)}
    return {bool: seed % 2 == 0, int: seed + 1, float: seed + 0.5, str: f"s{seed}"}.get(
        tp, date(2026, 1, 1 + seed % 28)
    )


@pytest.mark.parametrize("name", sorted(stageio.STAGE_FILES))
def test_stage_file_round_trips(name: str, tmp_path: Path) -> None:
    paths = Paths.for_root(tmp_path)
    spec = stageio.STAGE_FILES[name]
    assert spec.producer in stage_names()
    value = example(stageio.file_type(name))
    if spec.shape == "rows":
        value = [value, example(stageio.file_type(name), 3)]
    stageio.dump_stage(paths, name, value)
    assert stageio.load_stage(paths, name) == (value if spec.shape != "list" else tuple(value))
    first = stageio.stage_path(paths, name).read_bytes()
    stageio.dump_stage(paths, name, stageio.load_stage(paths, name))
    assert stageio.stage_path(paths, name).read_bytes() == first


def test_alias_index_round_trips(tmp_path: Path) -> None:
    index = {
        ("npm", "fontsourceinter"): ("inter", "package", ""),
        ("font-name", "sauceocodepro"): ("source-code-pro", "build", "nerd"),
        ("font-name", "arial"): ("", "ineligible", "proprietary"),
    }
    paths = Paths.for_root(tmp_path)
    stageio.dump_stage(paths, "alias_index", entries_of(index))
    assert index_of(stageio.load_stage(paths, "alias_index")) == index
    with pytest.raises(ValueError, match="twice"):
        index_of([IndexEntry("npm", "a", "x", "rename"), IndexEntry("npm", "a", "y", "rename")])


@pytest.mark.parametrize(
    ("tp", "value", "message"),
    [
        (IndexEntry, {"ns": "npm", "match_key": "a", "family_id": "x"}, "missing ['relation'"),
        (
            IndexEntry,
            {
                "ns": "npm",
                "match_key": "a",
                "family_id": "x",
                "relation": "r",
                "detail": "",
                "extra": 1,
            },
            "unknown ['extra']",
        ),
        (dict[str, float], {"a": "1"}, "expected float"),
        (dict[str, int], {"a": True}, "expected int"),
        (tuple[int, int], [1], "expected 2 items"),
        (Literal["A", "B"], "C", "not one of"),
        (date, "2026-13-01", "month"),
        (int | None, "x", "expected int"),
        (str, None, "expected str"),
    ],
)
def test_decode_is_strict(tp: Any, value: Any, message: str) -> None:
    with pytest.raises(stageio.StageFileError, match=message.replace("[", r"\[")):
        stageio.decode(tp, value)


def test_encode_refuses_what_json_cannot_hold() -> None:
    with pytest.raises(TypeError, match="map keys"):
        stageio.encode({1: "a"})
    with pytest.raises(TypeError, match="can't go"):
        stageio.encode({"a": {1, 2}})
    with pytest.raises(ValueError, match="not valid JSON"):
        stageio.encode(float("nan"))


def _realistic(name: str) -> object:
    if name == "terms":
        return {
            "desktop_chosen": {
                "homebrew": {"inter": Term(12.0, "observed", "homebrew")},
                "github": {
                    "jetbrains-mono": Term(3.0, "observed", "homebrew"),  # gate M5: same group
                    "inter": Term(None, "not_covered", "github_counters", "outside_frame"),
                },
            },
            "project": {
                "almanac": {
                    "barlow": Term(900.0, "observed", "http_archive", None, 0.5, ("parent_merge",)),
                    "inter": Term(2.0, "censored", "http_archive", "below_floor"),
                }
            },
        }
    if name == "ruler_counts":
        return {"inter": 5066.0, "jetbrains-mono": 0.0}
    raise AssertionError(name)


@pytest.mark.parametrize("name", sorted(n for n, s in stageio.STAGE_FILES.items() if s.schema))
def test_stage_file_matches_its_schema(name: str, tmp_path: Path) -> None:
    paths = Paths.for_root(tmp_path)
    stageio.dump_stage(paths, name, _realistic(name))
    schema = json.loads((ROOT / "schemas" / stageio.STAGE_FILES[name].schema).read_text("utf-8"))
    doc = json.loads(stageio.stage_path(paths, name).read_text("utf-8"))
    validator = Draft202012Validator(schema)
    assert [e.message for e in validator.iter_errors(doc)] == []
    assert stageio.load_stage(paths, name) == _realistic(name)
    if name == "terms":
        doc["project"]["almanac"]["inter"]["group"] = "chocolatey"  # gate T3: not a group
        assert not validator.is_valid(doc)
