"""Stage "universe": the candidate families (milestone-1 step 4). Owner: agent P1.

Builds one family per Google-Fonts-style family from the universe collectors'
records, using ``data/aliases.csv`` to fold renames, builds and packages into
their family. Each family keeps the id in ``state/ids.json``; a new family gets
``names.mint_id`` once, and a rename only adds an alias. Non-text families are
kept with a ``drop`` reason code, never silently removed.

Writes ``build/stage/universe.json``, ``build/universe.md`` (per-source counts,
drop reasons, every name mapped) and ``build/state/ids.json``.
Committed reports show sources whose ``publish_raw`` is false (Google and
Fonts Over Time, rulings T2 and T4) only as ranks or z scores, never as values.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tff_catalog.records import SourceKey

if TYPE_CHECKING:
    from tff_catalog.aliases import AliasTable
    from tff_catalog.records import UniverseRecord
    from tff_catalog.stages import StageContext


@dataclass(frozen=True, slots=True)
class Family:
    id: str
    family: str  # current display name
    keys: tuple[SourceKey, ...]  # every universe key that maps here, sorted
    sources: tuple[str, ...]  # universe collectors that list it, sorted
    first_seen: date
    minted_from: str  # the name the id was minted from
    drop: str | None = None  # records.DROP_REASONS code when out of the universe
    urls: tuple[tuple[str, str], ...] = ()  # (role, url), sorted


@dataclass(frozen=True, slots=True)
class Universe:
    families: dict[str, Family]  # by id, including dropped ones
    unmapped: tuple[SourceKey, ...]  # universe keys that reached no family (must be empty)

    def by_key(self, key: SourceKey) -> Family | None:
        raise NotImplementedError("M1 step 4")

    def eligible(self) -> dict[str, Family]:
        """Families without a ``drop`` reason."""
        raise NotImplementedError("M1 step 4")


def build_universe(
    recs: Iterable[UniverseRecord], aliases: AliasTable, ids: Mapping[str, Mapping[str, Any]]
) -> Universe:
    """Group universe records into families. Deterministic; never guesses a match."""
    raise NotImplementedError("M1 step 4")


def next_ids(u: Universe, ids: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """``ids.json`` for ``build/state/``: the old registry plus newly minted ids (append-only)."""
    raise NotImplementedError("M1 step 4")


def report(u: Universe) -> str:
    """``build/universe.md``: per-source counts, drop reasons, and every name mapped."""
    raise NotImplementedError("M1 step 4")


def load_universe(path: Path) -> Universe:
    """Read ``build/stage/universe.json``."""
    raise NotImplementedError("M1 step 4")


def dump_universe(u: Universe, path: Path) -> None:
    """Write ``build/stage/universe.json`` deterministically."""
    raise NotImplementedError("M1 step 4")


def run(ctx: StageContext) -> None:
    """Stage "universe"."""
    raise NotImplementedError("M1 step 4")
