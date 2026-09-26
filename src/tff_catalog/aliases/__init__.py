"""The alias table and the "aliases" stage (milestone-1 step 7). Owner of the stage: agent P4.

``data/aliases.csv`` is the one versioned table that maps every package, slug
and name to a family (design-m1 gap G5). Columns, in order::

    alias,ns,family_id,relation,detail,source,first_seen,reviewed_by

- ``alias`` + ``ns``: the name as written and its namespace (``records.NAMESPACES``);
  ``inter`` can be an npm, Fontsource and Google key at once, so ``ns`` is required.
- ``family_id``: the target family; empty only for ``ineligible`` rows. For
  ``distinct`` rows it is the family the alias must never map to.
- ``relation``: one of ``RELATIONS``.
- ``detail``: the ineligible reason (``INELIGIBLE_REASONS``), the build subtype
  (``BUILD_DETAILS``), or free text for the other relations.
- ``source``: the miner or person that proposed the row; ``first_seen``: ISO
  date; ``reviewed_by``: who accepted it (``auto:<rule>`` for auto-accepted).

Miners never write this file: they write ``data/alias-seeds/<miner>.csv``
(``SEED_COLUMNS``), and ``tff-catalog aliases --apply`` (the lead only) merges
accepted rows here. ``load_aliases`` and ``write_aliases`` are strict and
deterministic.
"""

import csv
import io
from collections.abc import Iterable
from dataclasses import astuple, dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from tff_catalog.jsonio import atomic_write
from tff_catalog.keys import match_key
from tff_catalog.names import ID_PATTERN
from tff_catalog.records import NAMESPACES, SourceKey

if TYPE_CHECKING:
    from tff_catalog.stages import StageContext

COLUMNS = ("alias", "ns", "family_id", "relation", "detail", "source", "first_seen", "reviewed_by")
SEED_COLUMNS = (
    "alias",
    "ns",
    "target_ns",
    "target",
    "relation",
    "detail",
    "source",
    "evidence",
    "auto",
)
RELATIONS = frozenset(
    {
        "rename",
        "build",
        "package",
        "postscript",
        "sibling",
        "related",
        "bundle",
        "distinct",
        "ineligible",
    }
)
INELIGIBLE_REASONS = frozenset({"proprietary", "itf", "cjk", "icon", "generic", "system"})
BUILD_DETAILS = frozenset(
    {
        "",
        "nerd",
        "nf",
        "nfm",
        "nfp",
        "propo",
        "powerline",
        "nl",
        "cjk",
        "variable",
        "static",
        "opsz",
    }
)


class AliasError(ValueError):
    """A malformed alias or seed file."""


@dataclass(frozen=True, slots=True, order=True)
class AliasRow:
    alias: str
    ns: str
    family_id: str
    relation: str
    detail: str
    source: str
    first_seen: date
    reviewed_by: str

    @property
    def key(self) -> SourceKey:
        return SourceKey(self.ns, self.alias)

    def problems(self) -> list[str]:
        """What is wrong with this row, if anything."""
        out = []
        if not self.alias or self.alias != self.alias.strip():
            out.append("alias is empty or has outer spaces")
        if self.ns not in NAMESPACES:
            out.append(f"unknown ns {self.ns!r}")
        if self.relation not in RELATIONS:
            out.append(f"unknown relation {self.relation!r}")
        if self.relation == "ineligible":
            if self.family_id:
                out.append("ineligible rows have no family_id")
            if self.detail not in INELIGIBLE_REASONS:
                out.append(f"ineligible reason {self.detail!r} not in {sorted(INELIGIBLE_REASONS)}")
        elif not ID_PATTERN.match(self.family_id):
            out.append(f"bad family_id {self.family_id!r}")
        if self.relation == "build" and self.detail not in BUILD_DETAILS:
            out.append(f"build detail {self.detail!r} not in {sorted(BUILD_DETAILS)}")
        if not self.source:
            out.append("source is empty")
        return out


def _sort_key(row: AliasRow) -> tuple[str, ...]:
    return (
        row.family_id,
        row.relation,
        row.ns,
        match_key(row.alias),
        row.alias,
        row.detail,
        row.source,
        row.first_seen.isoformat(),
        row.reviewed_by,
    )


def _read_csv(path: Path, columns: tuple[str, ...]) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if header is None or tuple(header) != columns:
            raise AliasError(f"{path}: header must be {','.join(columns)}")
        rows = []
        for number, values in enumerate(reader, start=2):
            if not values:
                continue
            if len(values) != len(columns):
                raise AliasError(
                    f"{path}:{number}: expected {len(columns)} fields, got {len(values)}"
                )
            rows.append(dict(zip(columns, values, strict=True)))
        return rows


def _write_csv(path: Path, columns: tuple[str, ...], rows: Iterable[tuple[str, ...]]) -> None:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(columns)
    writer.writerows(rows)
    atomic_write(Path(path), buf.getvalue().encode("utf-8"))


def load_aliases(path: Path) -> list[AliasRow]:
    """Read and validate ``data/aliases.csv``; raises ``AliasError`` naming the line."""
    out: list[AliasRow] = []
    seen: set[AliasRow] = set()
    for number, d in enumerate(_read_csv(path, COLUMNS), start=2):
        try:
            row = AliasRow(**{**d, "first_seen": date.fromisoformat(d["first_seen"])})
        except ValueError as exc:
            raise AliasError(f"{path}:{number}: {exc}") from exc
        problems = row.problems()
        if problems:
            raise AliasError(f"{path}:{number}: {'; '.join(problems)}")
        if row in seen:
            raise AliasError(f"{path}:{number}: duplicate row")
        seen.add(row)
        out.append(row)
    return out


def write_aliases(rows: Iterable[AliasRow], path: Path) -> None:
    """Validate and write ``rows`` in canonical order (by family, relation, ns, key)."""
    rows = sorted(set(rows), key=_sort_key)
    for row in rows:
        problems = row.problems()
        if problems:
            raise AliasError(f"{row.ns}:{row.alias}: {'; '.join(problems)}")
    _write_csv(
        path,
        COLUMNS,
        (tuple(v.isoformat() if isinstance(v, date) else v for v in astuple(row)) for row in rows),
    )


# --- miner output: data/alias-seeds/<miner>.csv ------------------------------------


@dataclass(frozen=True, slots=True, order=True)
class AliasCandidate:
    """A proposed alias. ``target`` names the family by one of its universe keys."""

    alias: SourceKey
    target: SourceKey
    relation: str
    detail: str
    source: str  # miner name
    evidence: str  # commit, URL or file that shows it
    auto: bool  # eligible for auto-accept (google/fonts renames, Nerd unpatchedName)


def load_seeds(path: Path) -> list[AliasCandidate]:
    """Read a miner's seed file."""
    out = []
    for number, d in enumerate(_read_csv(path, SEED_COLUMNS), start=2):
        if d["auto"] not in ("true", "false"):
            raise AliasError(f"{path}:{number}: auto must be true or false")
        cand = AliasCandidate(
            alias=SourceKey(d["ns"], d["alias"]),
            target=SourceKey(d["target_ns"], d["target"]),
            relation=d["relation"],
            detail=d["detail"],
            source=d["source"],
            evidence=d["evidence"],
            auto=d["auto"] == "true",
        )
        bad = [k.ns for k in (cand.alias, cand.target) if k.ns not in NAMESPACES]
        if bad or cand.relation not in RELATIONS:
            raise AliasError(f"{path}:{number}: bad namespace {bad} or relation {cand.relation!r}")
        out.append(cand)
    return out


def write_seeds(cands: Iterable[AliasCandidate], path: Path) -> None:
    """Write a miner's seed file, sorted and de-duplicated."""
    _write_csv(
        path,
        SEED_COLUMNS,
        (
            (
                c.alias.key,
                c.alias.ns,
                c.target.ns,
                c.target.key,
                c.relation,
                c.detail,
                c.source,
                c.evidence,
                "true" if c.auto else "false",
            )
            for c in sorted(set(cands))
        ),
    )


# --- the stage (agent P4) -------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AliasTable:
    """``aliases.csv`` indexed for lookups."""

    rows: tuple[AliasRow, ...]

    @classmethod
    def from_rows(cls, rows: Iterable[AliasRow]) -> AliasTable:
        """Index rows; raises ``AliasError`` when one (ns, match_key) maps to two families."""
        raise NotImplementedError("M1 step 7")

    def lookup(self, key: SourceKey) -> tuple[AliasRow, ...]:
        """Rows whose ``ns`` equals ``key.ns`` and whose ``match_key`` equals ``match_key(key.key)``."""
        raise NotImplementedError("M1 step 7")


def mine_all(ctx: StageContext) -> list[AliasCandidate]:
    """Run every miner (``aliases.miners.discover()``) and read ``data/alias-seeds/``."""
    raise NotImplementedError("M1 step 7")


def merge(
    table: AliasTable, cands: Iterable[AliasCandidate], auto_rules: frozenset[str]
) -> tuple[list[AliasRow], list[AliasCandidate]]:
    """Accept auto-eligible candidates under ``auto_rules``; return (rows, review queue)."""
    raise NotImplementedError("M1 step 7")


def run(ctx: StageContext) -> None:
    """Stage "aliases": write ``stage/alias_candidates.jsonl``, ``stage/alias_index.json``
    and ``stage/queues/aliases.json``. Never writes ``data/aliases.csv``.

    The index is written with ``stageio.dump_stage(paths, "alias_index",
    mapping.entries_of(index))``, the format stage "map" reads.
    """
    raise NotImplementedError("M1 step 7")


def cmd_queue(ctx: StageContext, *, count: bool = False) -> int:
    """``aliases --queue [--count]``: print the review queue (or its size)."""
    raise NotImplementedError("M1 step 7")


def cmd_apply(ctx: StageContext) -> int:
    """``aliases --apply``: merge accepted rows and owner rulings into ``data/aliases.csv``."""
    raise NotImplementedError("M1 step 7")
