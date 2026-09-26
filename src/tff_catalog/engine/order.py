"""Ordering, the evidence gate and bands (methodology §4 and §6, design-m1 §6). Owner: agent P7."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Scored:
    id: str
    name: str
    score: float  # S
    weight: float  # Σ w'
    ruler_z: float | None
    observed: int
    groups: int  # distinct independence groups among observed terms


@dataclass(frozen=True, slots=True)
class Placement:
    order: int  # exact position, always an integer
    rank: int | None  # 1-100 inside the exact top, else None
    band: str | None  # "101-250", "251-500", "501+"
    gate_held: bool  # the 2-group gate kept it out of the top 100


def ranked(f: Scored, min_observed: int = 1) -> bool:
    """Ranked at all: at least ``min_observed`` observed terms."""
    raise NotImplementedError("M1 step 11")


def gate(f: Scored, groups: int = 2) -> bool:
    """The top-100 evidence gate: observed terms from at least ``groups`` groups."""
    raise NotImplementedError("M1 step 11")


def sort_key(f: Scored) -> tuple[float, float, float, str, str]:
    """(-S, -Σw', -z_R or +inf, casefold(name), id): deterministic ties."""
    raise NotImplementedError("M1 step 11")


def place(
    ordered: Sequence[Scored],
    passes_gate: Mapping[str, bool],
    exact_top: int = 100,
    bands: Sequence[tuple[int, int]] = ((101, 250), (251, 500)),
    open_band_from: int = 501,
) -> dict[str, Placement]:
    """Assign orders, exact ranks and bands. Gate failures inside the top move to
    just after ``exact_top``, keeping their relative order."""
    raise NotImplementedError("M1 step 11")
