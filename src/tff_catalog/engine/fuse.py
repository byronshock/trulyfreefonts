"""Fusion with shrinkage and the outlier guard (methodology §4, design-m1 §6). Owner: agent P7."""

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Fused:
    score: float  # S
    weight: float  # Σ w' over the terms used (after guard factors)
    terms: int  # observed + censored terms
    observed: int  # observed terms only
    groups: tuple[str, ...]  # distinct independence groups among observed terms, sorted
    guard: tuple[tuple[str, float], ...] = ()  # (source, factor) where the guard fired


def guard_factors(
    terms: Mapping[str, float], gap: float = 1.5, min_terms: int = 3, factor: float = 0.5
) -> dict[str, float]:
    """Per-source weight factors: ``factor`` for a term more than ``gap`` z from the
    unweighted mean of the others, when there are at least ``min_terms`` terms.
    Applied simultaneously; 1.0 everywhere else."""
    raise NotImplementedError("M1 step 11")


def fuse(
    terms: Mapping[str, float],
    w_eff: Mapping[str, float],
    w_total: float,
    kappa: float,
    mu0: float,
    guard: Mapping[str, float] | None = None,
    groups: Mapping[str, str] | None = None,
    observed: frozenset[str] = frozenset(),
) -> Fused:
    """S = (κ·W·μ0 + Σ w'z) / (κ·W + Σ w') over the observed and censored terms.

    ``w_total`` is W_g, the survey's effective weight total (constant per
    survey); ``w_eff`` already includes each term's ``corrections.Term.factor``
    (so w' = w_eff * factor * guard factor). ``groups`` maps source to the
    family's independence group (``Term.group``, per family under gate M5) and
    ``observed`` names the observed (not censored) terms.
    """
    raise NotImplementedError("M1 step 11")
