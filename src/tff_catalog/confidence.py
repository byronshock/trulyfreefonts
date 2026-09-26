"""Stage "confidence": rank ranges and tiers (methodology §6, milestone-1 step 13). Owner: agent P10.

``rng = numpy.random.default_rng(ranking.toml [uncertainty].seed)``; per
survey, with sources sorted, ``d = rng.dirichlet(concentration · w_eff / W)``
and ``w* = d · W``: ``runs`` draws plus one leave-one-source-out run per
source; the 5-95% range uses ``numpy.quantile(..., method="inverted_cdf")``.
M_g is not perturbed.

Writes ``build/stage/confidence.json`` ({rank key: {id: Confidence}}).
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from tff_catalog.config_model import Tiers, Uncertainty
    from tff_catalog.stages import StageContext
    from tff_catalog.surveys import RankInputs

Range = tuple[int, int]
Tier = Literal["A", "B", "C"]


@dataclass(frozen=True, slots=True)
class Confidence:
    """One ranked font's range and tier in one rank key."""

    range: Range  # (p5, p95) ranks
    tier: Tier


def perturb(inputs: RankInputs, cfg: Uncertainty) -> dict[str, dict[str, Range]]:
    """{rank key: {family_id: (p5, p95)}} from the weight perturbations."""
    raise NotImplementedError("M1 step 13")


def tier(rank: int, width: int, groups: int, cfg: Tiers) -> Tier:
    """A: groups >= a_min_groups and width <= max(a_min_width, a_rank_share·rank); B: width <= b_rank_share·rank; else C."""
    raise NotImplementedError("M1 step 13")


def tiers(
    ranges: Mapping[str, Mapping[str, Range]],
    orders: Mapping[str, Mapping[str, int]],
    groups: Mapping[str, int],
    cfg: Tiers,
) -> dict[str, dict[str, Tier]]:
    """Tiers for every ranked font of every rank key."""
    raise NotImplementedError("M1 step 13")


def run(ctx: StageContext) -> None:
    """Stage "confidence"."""
    raise NotImplementedError("M1 step 13")
