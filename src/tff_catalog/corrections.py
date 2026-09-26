"""Stage "correct": confound corrections and evidence states (milestone-1 step 10). Owner: agent P6.

Turns mapped values into one term per (view, source, family):

- sums a family's packages and aliases, with Nerd, CJK and bundle credits;
- subtracts noise floors (Homebrew, including the gate-M3 Nerd floor; the Arch
  Nerd group floor; Nerd release deltas) and censors values under the floor;
- counts exposure from each channel's data date ("too new" under 60 days);
- makes Linux sources abstain, in every view except ``desktop_installed``, for
  fonts a Linux system preinstalls or whose top reverse dependency holds at
  least ``dependency_abstain`` of its installs;
- tags ``preinstalled_on`` and ``pulled_in_by``;
- gives each term its family's independence group (gate M5) and its weight
  factor and flags (the Almanac parent merge).

Writes:

- ``build/stage/terms.json``: {view: {source: {id: Term}}}, schema
  ``schemas/stage/terms.schema.json``;
- ``build/stage/ruler_counts.json``: {id: count}, the ruler's input
  (``ruler_counts``), schema ``schemas/stage/ruler_counts.schema.json``;
- ``build/stage/tags.json`` ({id: Tags}) and ``build/corrections.md``;
- its part of the next state, ``first_seen`` (``state.write_part``).

``build/corrections.md`` is committed: sources whose ``publish_raw`` is false
(Google and Fonts Over Time, rulings T2 and T4) appear in it only as ranks or
z scores, never as values.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from tff_catalog.config_model import Corrections, PreinstalledConfig, SourceBase
    from tff_catalog.mapping import Mapped
    from tff_catalog.records import Relation
    from tff_catalog.stages import StageContext

EvidenceState = Literal["observed", "censored", "not_covered", "too_new"]
Reason = Literal["below_floor", "no_value", "no_package", "outside_frame", "merged_into_parent"]
# Flags a term may carry; review.md lists them. Owner of this list: agent P6.
TERM_FLAGS = frozenset(
    {
        "parent_merge",  # Almanac: the name regex folded width cuts into this parent (§5)
        "bundle_only",  # counted only through a bundle (D2)
        "dependency_review",  # a Linux dependent holds 35-50% of installs (gate M8)
        "stale_sync",  # ecosyste.ms last_synced_at older than stale_sync_days
    }
)


@dataclass(frozen=True, slots=True)
class Term:
    """One family's evidence from one engine source in one view.

    - ``value``: after credits and floors; None unless observed or censored.
    - ``group``: the family's independence group for this source: the source's
      ``group``, except that the GitHub counters (``github``, ``nerd``) take
      ``homebrew`` for a family whose Homebrew cask downloads that repository's
      release asset (gate M5 (a), ``engine.github_homebrew_same_group``). The
      2-group gate and tier A count distinct groups among observed terms.
    - ``factor``: a weight multiplier for this family. The engine uses
      w' = w_eff * factor * guard factor. The Almanac parent merge ("flagged and
      halved", methodology §5) is ``factor = almanac.parent_merge_factor`` plus
      the flag ``parent_merge``; it never changes ``value``.
    - ``flags``: sorted, from ``TERM_FLAGS``.
    """

    value: float | None
    state: EvidenceState
    group: str  # records.GROUPS
    reason: Reason | None = None
    factor: float = 1.0
    flags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Tags:
    """One family's tags, ``build/stage/tags.json`` ({id: Tags})."""

    preinstalled_on: tuple[str, ...] = ()  # preinstalled.toml system ids, sorted
    pulled_in_by: tuple[tuple[str, str], ...] = ()  # (system, package), sorted
    flags: tuple[str, ...] = ()  # "no_deliberate_evidence" when abstentions left no desktop term


@dataclass(frozen=True, slots=True)
class Abstention:
    source: str
    family_id: str
    why: Literal["preinstalled", "dependency"]
    system: str  # the preinstalled system, or the dependency's distribution
    package: str | None = None  # the pulling package
    share: float | None = None  # its share of installs


def sum_aliases(mapped: Iterable[Mapped], cfg: Corrections) -> dict[str, dict[str, float]]:
    """{source: {family_id: value}} with packages summed and build/bundle credits applied."""
    raise NotImplementedError("M1 step 10")


def apply_credits(
    values: Mapping[str, float], details: Mapping[str, str], cfg: Corrections
) -> dict[str, float]:
    """Nerd, CJK and bundle credits (a build that is both NF and CN takes the smaller)."""
    raise NotImplementedError("M1 step 10")


def apply_floors(values: Mapping[str, float], src: SourceBase) -> dict[str, Term]:
    """Subtract the source's floor and censor values under ``censor_below``."""
    raise NotImplementedError("M1 step 10")


def exposure(first_seen: date | None, data_date: date, min_days: int) -> bool:
    """Whether a channel has seen the font long enough (``False`` means "too new")."""
    raise NotImplementedError("M1 step 10")


def ruler_counts(credited: Mapping[str, float], cask_families: Iterable[str]) -> dict[str, float]:
    """The ruler's input (methodology §3, design-m1 §6), written to ``build/stage/ruler_counts.json``.

    Homebrew 365-day installs per family after the Latin and license gates,
    alias sums and credits, with **no floor** (neither the flat floor nor the
    gate-M3 Nerd floor), and 0 for a family with a cask but no analytics row.
    ``credited`` is ``sum_aliases`` output for ``homebrew``; ``cask_families``
    are the eligible families that have a Homebrew cask.
    """
    raise NotImplementedError("M1 step 10")


def abstentions(
    deps: Iterable[Relation],
    counts: Mapping[str, Mapping[str, float]],
    preinst: PreinstalledConfig,
    cfg: Corrections,
) -> dict[str, dict[str, Abstention]]:
    """{source: {family_id: Abstention}} for the Linux sources (D8, gate M8)."""
    raise NotImplementedError("M1 step 10")


def run(ctx: StageContext) -> None:
    """Stage "correct"."""
    raise NotImplementedError("M1 step 10")
