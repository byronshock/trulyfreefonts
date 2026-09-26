"""Monthly cross-checks (decisions D1 and D5, design-m1 §6). Owner: agent P7b.

- Coverage-aware reciprocal-rank fusion (k=60): each font averaged over only
  the sources that cover it, plus a prior.
- A rerun with Fontsource (jsDelivr) as the ruler.

Moves over ``ranking.toml [crosscheck] move_flag`` are flagged in review.md.
"""

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Move:
    id: str
    rank: int
    other: int
    change: float  # |rank - other| / rank


def rrf(
    ranks: Mapping[str, Mapping[str, int]], weights: Mapping[str, float], k: int = 60
) -> dict[str, float]:
    """Coverage-aware RRF: ``ranks`` is {source: {id: rank in source}}."""
    raise NotImplementedError("M1 step 11")


def rerun_with_ruler(inputs: object, ruler: str) -> dict[str, int]:
    """Re-rank ``inputs`` (``surveys.RankInputs``) with engine source ``ruler`` as the ruler."""
    raise NotImplementedError("M1 step 11")


def moves(
    ranks: Mapping[str, int], other: Mapping[str, int], threshold: float = 0.30
) -> list[Move]:
    """Fonts whose rank moves by more than ``threshold`` (relative), sorted by rank."""
    raise NotImplementedError("M1 step 11")
