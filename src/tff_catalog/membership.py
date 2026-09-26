"""Stage "membership": catalog membership with hysteresis (milestone-1 step 12). Owner: agent P8.

The catalog is the overall top ``catalog_size`` plus the top ``extra_top`` of
each of ``extra_ranks``. A font enters at ``enter`` or better and leaves after
``leave_runs`` runs worse than ``leave``; each top-100 list has its own
hysteresis (gate M11). Counters advance once per merged run, never twice.

Writes ``build/stage/membership.json`` and ``build/state/membership.json``.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tff_catalog.config_model import Membership as MembershipConfig
    from tff_catalog.stages import StageContext


@dataclass(frozen=True, slots=True)
class MemberState:
    member: bool
    entered: date | None
    runs_outside: int


@dataclass(frozen=True, slots=True)
class Membership:
    catalog: Mapping[str, MemberState]  # by family_id
    top100: Mapping[str, Mapping[str, MemberState]]  # {rank key: {family_id: state}}


def update(
    ranks: Mapping[str, Mapping[str, int]],
    prev: Membership,
    cfg: MembershipConfig,
    run_date: date,
) -> Membership:
    """Next membership from this run's orders ({rank key: {family_id: order}})."""
    raise NotImplementedError("M1 step 12")


def run(ctx: StageContext) -> None:
    """Stage "membership"."""
    raise NotImplementedError("M1 step 12")
