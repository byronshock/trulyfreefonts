"""Stage "rank": per-survey scores, the overall rank and the views (milestone-1 steps 11-12). Owner: agent P8.

For each rank key (``config_model.RANK_KEYS``): equate each source to the
ruler, weight it (``effective_weights``), fuse with shrinkage and the guard,
then order, gate and band. The overall rank reuses the ``desktop_chosen`` and
``project`` terms, weighted v_s = M_g·w'_s/W_g and shrunk once (Σ M_g = 1),
with each survey's guard factors reused. Extra views never feed overall.

Reads ``build/stage/terms.json`` and ``build/stage/ruler_counts.json`` (stage
"correct"): z_R comes from the ruler counts (``equate.build_ruler``), never
from the floored Homebrew terms. Independence groups come from each
``Term.group`` (gate M5 makes them per family). Writes ``build/stage/ruler.json``,
``build/stage/scores.json`` (with guard events) and ``build/stage/ranks.json``,
and its part of the next state, ``smoothing`` (``state.write_part``).
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tff_catalog.corrections import Term
from tff_catalog.engine.fuse import Fused
from tff_catalog.engine.order import Placement

if TYPE_CHECKING:
    from tff_catalog.config_model import RankingConfig, RisingView
    from tff_catalog.stages import StageContext

# {source: {family_id: Term}} for one view.
type Terms = Mapping[str, Mapping[str, Term]]


@dataclass(frozen=True, slots=True)
class RankInputs:
    """Everything needed to (re)compute the ranks; confidence perturbs ``weights``."""

    terms: Mapping[str, Terms]  # {rank key: terms}; each Term carries its group and factor
    ruler: Mapping[str, float]  # z_R by family, from build/stage/ruler_counts.json
    weights: Mapping[str, Mapping[str, float]]  # {rank key: {source: weight}} (effective_weights)
    names: Mapping[str, str]  # family_id -> family name (tie order)


@dataclass(frozen=True, slots=True)
class SurveyScores:
    key: str  # rank key
    fused: Mapping[str, Fused]  # by family_id
    placements: Mapping[str, Placement]
    overlaps: Mapping[str, int]  # source -> |O_s|
    weights: Mapping[str, float]  # source -> w_eff


def effective_weights(
    cfg: RankingConfig,
    key: str,
    overlaps: Mapping[str, int],
    stale_dropped: frozenset[str],
    phase_in: Mapping[str, bool],
) -> dict[str, float]:
    """The weight of each engine source in rank key ``key``.

    First, for every source: w_eff = w · overlap_scale(|O_s|) · (0 if the source
    is disabled or stale-dropped), where w is the nominal weight
    (``surveys.<survey>.weights`` or ``ranks.<view>.weights``) and a phasing-in
    source (Fonts Over Time before ``phase_in_snapshots``) uses its
    ``phase_in_weight`` in place of w.

    Then, for the project survey only (``project``, and the project part of
    ``overall``), gate M9 (b): each group G in ``project_group_shares`` keeps
    its fixed share, split pro rata inside the group:
    w_s = share_G · w_eff_s / Σ_{t∈G} w_eff_t. A group whose effective weights
    are all 0 contributes nothing, so W_project is the sum of the other groups'
    shares. Desktop and the extra views use w_eff as it is.

    W_g, the total used for shrinkage, is the sum of the returned weights.
    """
    raise NotImplementedError("M1 step 11")


def score_survey(
    terms: Terms, weights: Mapping[str, float], ruler: Mapping[str, float], cfg: RankingConfig
) -> SurveyScores:
    """Equate, fuse, order and place one survey or view."""
    raise NotImplementedError("M1 step 11")


def overall(inputs: RankInputs, cfg: RankingConfig) -> SurveyScores:
    """The overall rank from the most-chosen desktop and project terms (D12)."""
    raise NotImplementedError("M1 step 12")


def views(inputs: RankInputs, cfg: RankingConfig) -> dict[str, SurveyScores]:
    """Every published rank key, including coding, dev_apps and rising."""
    raise NotImplementedError("M1 step 12")


def rising(history: Mapping[str, Mapping[str, list[float]]], cfg: RisingView) -> dict[str, float]:
    """Rising (beta): smoothed log-ratio of recent to 12-month share, 2 sources agreeing."""
    raise NotImplementedError("M1 step 12")


def run(ctx: StageContext) -> None:
    """Stage "rank"."""
    raise NotImplementedError("M1 step 11")
