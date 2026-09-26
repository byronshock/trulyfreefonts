"""tff_catalog.keys against the shared vector file tests/vectors/name-keys.json."""

import json
import sys
import unicodedata
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tff_catalog.keys import DROP_CODEPOINTS, expand_codepoints, match_key, search_key

VECTORS = Path(__file__).parent / "vectors" / "name-keys.json"
DATA = json.loads(VECTORS.read_text(encoding="utf-8"))
CASES = DATA["cases"]
CASE_IDS = [f"{i:02d}-{case['input']}" for i, case in enumerate(CASES)]
DROPPED = expand_codepoints(DROP_CODEPOINTS)


def test_vector_file_header():
    assert DATA["format"] == "tff-name-keys"
    assert DATA["version"] == 1
    assert set(DATA["spec"]) == {"match_key", "search_key", "drop_codepoints", "casefold_extra"}
    assert len(CASES) >= 40
    inputs = [case["input"] for case in CASES]
    assert len(set(inputs)) == len(inputs), "duplicate inputs"
    for case in CASES:
        assert set(case) <= {"input", "match_key", "search_key", "note"}


def test_drop_codepoints_constant_equals_file():
    assert list(DROP_CODEPOINTS) == DATA["spec"]["drop_codepoints"]


def _python_casefold_extra() -> dict[str, str]:
    """Code points that can follow NFKC whose casefold differs from lower() plus ß/ς."""
    table = {}
    for cp in range(sys.maxunicode + 1):
        if 0xD800 <= cp <= 0xDFFF:
            continue
        ch = chr(cp)
        if unicodedata.category(ch) == "Cn" or not unicodedata.is_normalized("NFKC", ch):
            continue
        if ch.casefold() != ch.lower().replace("\u00df", "ss").replace("\u03c2", "\u03c3"):
            table[f"{cp:04X}"] = " ".join(f"{ord(x):04X}" for x in ch.casefold())
    return table


def test_casefold_extra_is_pythons_casefold():
    """The JavaScript port's casefold table (site/js/05-keys.js must equal it too)."""
    assert DATA["spec"]["casefold_extra"] == _python_casefold_extra()


def _js_style_casefold(s: str) -> str:
    extra = DATA["spec"]["casefold_extra"]
    out = []
    for ch in s:
        mapped = extra.get(f"{ord(ch):04X}")
        if mapped is None:
            out.append(ch.lower().replace("\u00df", "ss").replace("\u03c2", "\u03c3"))
        else:
            out.append("".join(chr(int(h, 16)) for h in mapped.split()))
    return "".join(out)


@settings(max_examples=400, derandomize=True, deadline=None)
@given(st.text(st.characters(), max_size=24))
def test_the_javascript_recipe_matches_casefold(s):
    nfkc = unicodedata.normalize("NFKC", s)
    js = unicodedata.normalize("NFKC", _js_style_casefold(nfkc))
    assert js == unicodedata.normalize("NFKC", nfkc.casefold())


def test_unicode_tables_are_new_enough():
    have = tuple(int(part) for part in unicodedata.unidata_version.split("."))
    need = tuple(int(part) for part in DATA["unicode_max"].split("."))
    assert have >= need


def test_inputs_use_only_assigned_code_points():
    unassigned = [
        (case["input"], f"U+{ord(ch):04X}")
        for case in CASES
        for ch in case["input"]
        if unicodedata.category(ch) == "Cn"
    ]
    assert unassigned == []


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_vector(case):
    assert match_key(case["input"]) == case["match_key"]
    assert search_key(case["input"]) == case["search_key"]


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_vector_keys_are_fixed_points(case):
    assert match_key(case["match_key"]) == case["match_key"]
    assert search_key(case["search_key"]) == case["search_key"]
    assert search_key(case["match_key"]) == case["search_key"]


# Arbitrary text, weighted towards the characters the keys treat specially.
_special = st.sampled_from(sorted(chr(cp) for cp in DROPPED))
_marks = st.characters(categories=["Mn"])
names = st.text(st.one_of(st.characters(), _special, _marks), max_size=24)


@settings(max_examples=400, derandomize=True, deadline=None)
@given(names)
def test_keys_are_idempotent(s):
    key = match_key(s)
    assert match_key(key) == key
    folded = search_key(s)
    assert search_key(folded) == folded
    assert search_key(key) == folded


@settings(max_examples=400, derandomize=True, deadline=None)
@given(names)
def test_key_output_shape(s):
    key = match_key(s)
    assert not DROPPED.intersection(map(ord, key))
    assert unicodedata.is_normalized("NFC", key)
    folded = search_key(s)
    assert not any(unicodedata.category(ch) == "Mn" for ch in folded)
    assert unicodedata.is_normalized("NFC", folded)
