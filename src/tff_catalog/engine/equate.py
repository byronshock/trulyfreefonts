"""The shared scale: the ruler and equating (methodology §3, design-m1 §6). Owner: agent P7."""

from collections.abc import Mapping


def build_ruler(counts: Mapping[str, float]) -> dict[str, float]:
    """z_R per family from ruler counts after gates, alias sums and credits, with no floor.

    Casks with no analytics row count 0. z_R = probit(midrank_p(x, all counts)).
    """
    raise NotImplementedError("M1 step 11")


def equate_source(xs: Mapping[str, float], ruler_z: Mapping[str, float]) -> dict[str, float]:
    """Map a source's values onto the ruler's scale.

    O_s = the families in both ``xs`` (observed and censored; censored are
    ``-inf``) and ``ruler_z``. For each f in ``xs``: p = midrank_p(x_f, xs over
    O_s), z_s(f) = hazen_quantile(sorted(z_R over O_s), p).
    """
    raise NotImplementedError("M1 step 11")


def overlap_scale(n: int, full: int = 50, off: int = 15) -> float:
    """Weight factor for a source overlapping the ruler on ``n`` families: 0 below ``off``, else min(1, n/full)."""
    raise NotImplementedError("M1 step 11")
