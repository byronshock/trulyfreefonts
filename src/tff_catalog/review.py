"""Stage "review": the monthly diff, the flags and the review pack (milestone-1 steps 15-16). Owner: agent P12b.

``build/review.md`` holds entries, exits, big moves, license changes and every
§9 flag (RBO and Spearman against last month, coverage changes, stale sources,
ruler overlaps and guard hits, share jumps, cross-check moves, the what-if
table, snapshot growth). ``build/review-pack/`` adds the top-100 lists with
tiers and per-source ranks for the owner's review (gate R).

``build/review.md`` is committed and public: sources whose ``publish_raw`` is
false (Google and Fonts Over Time, rulings T2 and T4) appear in it only as
ranks or z scores. ``build/review-pack/`` is gitignored (owner only).
"""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tff_catalog.stages import StageContext


@dataclass(frozen=True, slots=True)
class Flag:
    kind: str  # "rbo", "spearman", "stale", "guard", "share_jump", "crosscheck", ...
    message: str
    rank_key: str | None = None
    family_id: str | None = None


def rbo(a: Sequence[str], b: Sequence[str], p: float = 0.98) -> float:
    """Rank-biased overlap of two orderings (extrapolated)."""
    raise NotImplementedError("M1 step 15")


def render_review(
    prev_ranks: Mapping[str, Mapping[str, int]],
    ranks: Mapping[str, Mapping[str, int]],
    flags: Iterable[Flag],
) -> str:
    """``build/review.md``."""
    raise NotImplementedError("M1 step 15")


def review_pack(ctx: StageContext) -> Path:
    """Write ``build/review-pack/`` and return its path."""
    raise NotImplementedError("M1 step 16")


def run(ctx: StageContext) -> None:
    """Stage "review"."""
    raise NotImplementedError("M1 step 15")
