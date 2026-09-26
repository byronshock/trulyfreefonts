"""Stage "map": source keys to families (milestone-1 step 9). Owner: agent P5.

Every ranking record's key is looked up in the alias index (exact
``match_key`` within its namespace, never by prefix). A key maps to one family,
to an ineligible row, or to nothing; nothing is guessed. Unmatched keys above
their source's floor go to ``build/unmatched.md``, sorted by volume.
``build/unmatched.md`` is committed, so a source whose ``publish_raw`` is false
(Google and Fonts Over Time, rulings T2 and T4) shows each key's rank in the
source, never its value.

Reads the alias index, ``build/stage/alias_index.json`` (stage "aliases";
``stageio.load_stage(paths, "alias_index")`` gives ``IndexEntry`` rows and
``index_of`` turns them into an ``AliasIndex``). Writes
``build/stage/mapped.jsonl`` (``stageio`` rows of ``Mapped``) and
``build/unmatched.md``.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tff_catalog.records import Observation, Relation, SourceKey

if TYPE_CHECKING:
    from tff_catalog.stages import StageContext


@dataclass(frozen=True, slots=True)
class Mapped:
    record: Observation | Relation
    family_id: str | None  # None for ineligible keys
    relation: str  # "direct" or the alias relation used
    detail: str = ""  # build subtype, bundle, ineligible reason


@dataclass(frozen=True, slots=True)
class Unmatched:
    source: str
    key: SourceKey
    value: float | None
    unit: str


# (ns, match_key) -> (family_id or "", relation, detail), from stage/alias_index.json.
type AliasIndex = Mapping[tuple[str, str], tuple[str, str, str]]


@dataclass(frozen=True, slots=True, order=True)
class IndexEntry:
    """One row of ``build/stage/alias_index.json`` (a JSON array, sorted)."""

    ns: str
    match_key: str
    family_id: str  # "" for ineligible names
    relation: str  # aliases.RELATIONS, or "direct"
    detail: str = ""


def index_of(entries: Iterable[IndexEntry]) -> dict[tuple[str, str], tuple[str, str, str]]:
    """The ``AliasIndex`` of the entries; a (ns, match_key) listed twice raises ``ValueError``."""
    index: dict[tuple[str, str], tuple[str, str, str]] = {}
    for e in entries:
        key = (e.ns, e.match_key)
        if key in index:
            raise ValueError(f"alias index lists {key} twice")
        index[key] = (e.family_id, e.relation, e.detail)
    return index


def entries_of(index: AliasIndex) -> list[IndexEntry]:
    """The sorted rows to write for ``index`` (the inverse of ``index_of``)."""
    return sorted(IndexEntry(ns, key, *value) for (ns, key), value in index.items())


def map_records(
    recs: Iterable[Observation | Relation], idx: AliasIndex
) -> tuple[list[Mapped], list[Unmatched]]:
    """Map every record; relations map both ends."""
    raise NotImplementedError("M1 step 9")


def unmatched_report(unmatched: Iterable[Unmatched], floors: Mapping[str, float]) -> str:
    """``build/unmatched.md``: keys above each source's floor, largest first."""
    raise NotImplementedError("M1 step 9")


def run(ctx: StageContext) -> None:
    """Stage "map"."""
    raise NotImplementedError("M1 step 9")


def cmd_check_unmatched(ctx: StageContext, *, top: int) -> int:
    """``map --check-unmatched N``: non-zero if any source has an unmatched key in its top N."""
    raise NotImplementedError("M1 step 9")
