"""Load and validate ``catalog-site.json``, and derive the two page payloads from it.

Validation has two layers, and ``tff-site validate`` and ``tff-site build`` run both:

- ``schema_errors``: JSON Schema 2020-12, ``schemas/catalog-site.schema.json``.
- ``semantic_errors``: the cross-references a schema can't express: unique ids, every rank
  key in ``views``, bands that tile 101 upwards, ``rank == order`` inside the top 100, band
  labels that match ``order``, license classes, systems and sources that exist, one source
  entry per source, ranks withheld for sources whose terms forbid them, and view universes
  (every font in every available view; ``coding`` holds exactly the monospace fonts).

The payloads (``list_index`` and ``details``) are the formats in ``site/CONTRACT.md``.
"""

import json
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "catalog-site.schema.json"
SCHEMA_VERSION = "1.0.0-draft"

# Versioned rank keys (methodology §7), in the rank selector's order.
RANK_KEYS = (
    "overall",
    "desktop_chosen",
    "desktop_installed",
    "project",
    "coding",
    "dev_apps",
    "rising",
)
# The only view whose universe is a subset of the catalog: monospace fonts.
MONOSPACE_VIEW = "coding"
# Linux sources never abstain here (D8): it counts every install.
NO_ABSTAIN_VIEW = "desktop_installed"
TOP_N = 100

# Page wording for the enums. The list index carries these, so the script holds no copy.
UNRANKED_LABELS = {
    "no_deliberate_evidence": "no evidence of deliberate installs",
    "no_evidence": "no evidence in this rank",
    "too_new": "too new to rank",
}
STATE_LABELS = {
    "observed": "observed",
    "censored": "below the floor",
    "not_covered": "not covered",
    "too_new": "too new",
}
SPECIMEN_FLAGS = frozenset({"specimen_failed", "specimen_name_only", "specimen_hash_mismatch"})
# Written by the sample until the specimens are rendered: the build treats it as no preview.
PLACEHOLDER_SHA256 = "0" * 64


class CatalogError(ValueError):
    """The catalog failed validation. ``errors`` holds one line per problem."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(f"{len(errors)} problem(s); first: {errors[0] if errors else '-'}")


@dataclass(frozen=True, slots=True)
class Validated:
    """What ``tff-site validate`` reports for a valid file."""

    version: str
    fonts: int


def load(path: Path) -> dict[str, Any]:
    """Read a catalog-site JSON file (UTF-8) without validating it."""
    with Path(path).open(encoding="utf-8") as fh:
        return json.load(fh)


def schema() -> dict[str, Any]:
    """Return the catalog-site JSON Schema."""
    with SCHEMA_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def schema_errors(doc: Any) -> list[str]:
    """Return JSON Schema violations as ``"<json path>: <message>"`` lines, in path order."""
    # Imported here so `tff-site --help` stays fast.
    from jsonschema import Draft202012Validator

    validator = Draft202012Validator(schema())
    found = sorted(validator.iter_errors(doc), key=lambda e: (e.json_path, e.message))
    return [f"{e.json_path}: {e.message}" for e in found]


def semantic_errors(doc: Mapping[str, Any]) -> list[str]:
    """Return cross-reference problems in a schema-valid document (see the module docstring)."""
    errors: list[str] = []
    views = doc["views"]
    view_keys = [v["key"] for v in views]
    errors += [f"views: {k!r} listed twice" for k in _dupes(view_keys)]
    errors += [f"views: rank key {k!r} missing" for k in RANK_KEYS if k not in view_keys]
    available = [v["key"] for v in views if v["available"]]
    errors += _band_errors(doc["bands"])
    band_labels = {b["label"] for b in doc["bands"]}

    source_ids = [s["id"] for s in doc["sources"]]
    errors += [f"sources: id {k!r} listed twice" for k in _dupes(source_ids)]
    publishes = {s["id"]: s["publish_rank"] for s in doc["sources"]}
    survey = {s["id"]: s["survey"] for s in doc["sources"]}
    system_os = {s["id"]: s["os"] for s in doc["systems"]}
    errors += [f"systems: id {k!r} listed twice" for k in _dupes(s["id"] for s in doc["systems"])]
    classes = {c["id"] for c in doc["license_classes"]}
    errors += [
        f"license_classes: id {k!r} listed twice"
        for k in _dupes(c["id"] for c in doc["license_classes"])
    ]

    fonts = doc["fonts"]
    errors += [f"fonts: id {k!r} listed twice" for k in _dupes(f["id"] for f in fonts)]
    orders: dict[str, Counter[int]] = {k: Counter() for k in view_keys}
    for i, font in enumerate(fonts):
        where = f"fonts[{i}] {font['id']}"
        errors += [f"{where}: {msg}" for msg in _font_errors(font, classes, system_os)]
        for key in available:
            present = key in font["ranks"]
            wanted = font["is_monospace"] if key == MONOSPACE_VIEW else True
            if present != wanted:
                errors.append(f"{where}: ranks.{key} {'unexpected' if present else 'missing'}")
        for key, entry in font["ranks"].items():
            errors += [f"{where}: ranks.{key}: {msg}" for msg in _rank_errors(entry, doc["bands"])]
            if entry["band"] is not None and entry["band"] not in band_labels:
                errors.append(f"{where}: ranks.{key}: unknown band {entry['band']!r}")
            if entry["order"] is not None and key in orders:
                orders[key][entry["order"]] += 1
        if set(font["sources"]) != set(source_ids):
            missing = sorted(set(source_ids) - set(font["sources"]))
            extra = sorted(set(font["sources"]) - set(source_ids))
            errors.append(f"{where}: sources: missing {missing}, unknown {extra}")
        for sid, entry in font["sources"].items():
            if entry["rank_in_source"] is not None and not publishes.get(sid, False):
                errors.append(f"{where}: sources.{sid}: rank_in_source for an unpublished source")
            if entry["abstains_in"]:
                if survey.get(sid) != "desktop":
                    errors.append(f"{where}: sources.{sid}: only desktop sources abstain")
                if NO_ABSTAIN_VIEW in entry["abstains_in"]:
                    errors.append(f"{where}: sources.{sid}: abstains in {NO_ABSTAIN_VIEW}")
                stray = sorted(set(entry["abstains_in"]) - set(font["ranks"]))
                if stray:
                    errors.append(f"{where}: sources.{sid}: abstains in views without it {stray}")
    for key, counts in orders.items():
        errors += [f"ranks.{key}: order {o} used by {n} fonts" for o, n in counts.items() if n > 1]
    return errors


def validate(doc: Any) -> Validated:
    """Run both layers; raise ``CatalogError`` listing every problem, or return the summary."""
    errors = schema_errors(doc)
    if not errors:
        errors = semantic_errors(doc)
    if errors:
        raise CatalogError(errors)
    return Validated(version=doc["schema_version"], fonts=len(doc["fonts"]))


def validate_file(path: Path) -> Validated:
    """``validate(load(path))``; a file that isn't JSON raises ``CatalogError`` too."""
    try:
        doc = load(path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogError([f"{path}: {exc}"]) from exc
    return validate(doc)


def band_of(order: int, bands: list[Mapping[str, Any]]) -> str | None:
    """Return the label of the band holding ``order``, or None inside the exact top 100."""
    for band in bands:
        if order >= band["from"] and (band["to"] is None or order <= band["to"]):
            return band["label"]
    return None


def list_index(doc: Mapping[str, Any], *, commit: str) -> dict[str, Any]:
    """Return the list-index payload (``/assets/list.<h>.json``; format in site/CONTRACT.md).

    Font index ``i`` is the ``i``-th server-rendered row: Overall order, then fonts unranked
    in Overall by Python ``str.casefold`` of the family, then id.
    """
    raise NotImplementedError("M2 step 1")


def details(doc: Mapping[str, Any], *, font_assets: Mapping[str, str]) -> dict[str, Any]:
    """Return the details payload (``/assets/details.<h>.json``; format in site/CONTRACT.md).

    ``font_assets`` maps font id to the hashed ``/assets/fonts/…`` URL of its font file.
    """
    raise NotImplementedError("M2 step 4")


def server_order(doc: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Return the fonts in server-rendered order (see ``list_index``)."""
    raise NotImplementedError("M2 step 1")


def _dupes(items: Iterable[str]) -> list[str]:
    return sorted(k for k, n in Counter(items).items() if n > 1)


def _band_errors(bands: list[Mapping[str, Any]]) -> list[str]:
    errors = [f"bands: label {k!r} listed twice" for k in _dupes(b["label"] for b in bands)]
    if bands[0]["from"] != TOP_N + 1:
        errors.append(f"bands: the first band must start at {TOP_N + 1}")
    for prev, band in pairwise(bands):
        if prev["to"] is None or band["from"] != prev["to"] + 1:
            errors.append(f"bands: {band['label']!r} doesn't follow {prev['label']!r}")
    errors += [
        f"bands: {band['label']!r} ends before it starts"
        for band in bands
        if band["to"] is not None and band["to"] < band["from"]
    ]
    if bands[-1]["to"] is not None:
        errors.append("bands: the last band must be open-ended (to: null)")
    return errors


def _rank_errors(entry: Mapping[str, Any], bands: list[Mapping[str, Any]]) -> list[str]:
    order = entry["order"]
    if order is None:
        return []
    errors = []
    if entry["rank"] is not None and entry["rank"] != order:
        errors.append(f"rank {entry['rank']} != order {order}")
    if (entry["rank"] is None) != (order > TOP_N):
        errors.append(f"order {order} needs {'a band' if order > TOP_N else 'an exact rank'}")
    if entry["band"] is not None and entry["band"] != band_of(order, bands):
        errors.append(f"band {entry['band']!r} doesn't hold order {order}")
    low, high = entry["range"]
    if low > high:
        errors.append(f"range {entry['range']} is reversed")
    return errors


def _font_errors(
    font: Mapping[str, Any], classes: set[str], system_os: Mapping[str, str]
) -> list[str]:
    errors = []
    if font["license"]["class"] not in classes:
        errors.append(f"license.class {font['license']['class']!r} isn't in license_classes")
    errors += [
        f"preinstalled_on: unknown system {item['system']!r}"
        for item in font["preinstalled_on"]
        if item["system"] not in system_os
    ]
    errors += [
        f"pulled_in_by: {item['system']!r} is not a Linux system"
        for item in font["pulled_in_by"]
        if system_os.get(item["system"]) != "linux"
    ]
    preview = font["preview"]
    if preview is not None and preview["path"] != f"specimens/{font['id']}.svg":
        errors.append(f"preview.path must be specimens/{font['id']}.svg")
    flags = set(font["flags"])
    if flags & SPECIMEN_FLAGS and not font["preview_ok"]:
        errors.append("specimen flags on a font without preview_ok")
    if flags & {"specimen_failed", "specimen_hash_mismatch"} and preview is not None:
        errors.append("a failed specimen can't have a preview")
    if "specimen_name_only" in flags and preview is None:
        errors.append("specimen_name_only needs a preview")
    too_new = any(e["unranked"] == "too_new" for e in font["ranks"].values())
    if too_new and "too_new" not in flags:
        errors.append("unranked as too_new without the too_new flag")
    return errors
