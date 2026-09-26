"""Rank statistics (design-m1 §6). Owner: agent P7."""

from collections.abc import Sequence


def probit(p: float) -> float:
    """Φ⁻¹(p): ``statistics.NormalDist().inv_cdf(p)``, for 0 < p < 1."""
    raise NotImplementedError("M1 step 11")


def midrank_p(x: float, pool_sorted: Sequence[float], include_self: bool) -> float:
    """Mid-rank percentile (L + U) / 2n of ``x`` in an ascending pool.

    L and U are counts: values < x and values <= x (``bisect_left`` and
    ``bisect_right``). When ``include_self`` is false, x is counted in (+1 on U
    and on n). Censored and missing-in-frame values are ``-inf``, so they form
    one tie block at the bottom and get p = c/2n automatically.
    """
    raise NotImplementedError("M1 step 11")


def hazen_quantile(sorted_values: Sequence[float], p: float) -> float:
    """The Hazen p-quantile: position h = n·p + 0.5, linear interpolation, clamped to the ends.

    It exactly inverts mid-ranks, so a source identical to the ruler maps onto
    the ruler's own z values.
    """
    raise NotImplementedError("M1 step 11")
