"""Render one specimen SVG with HarfBuzz (design-m2 §3). Owner: agent A5.

- ``uharfbuzz`` Buffer, ``guess_segment_properties``, ``shape`` with default features.
- Variation: ``wght=400`` when 400 is inside the axis range, else the default instance.
- ``font.draw_glyph_with_pen(gid, RelPathPen)``, one pen across all lines
  (relative ``m`` commands continue across lines).
- Integer coordinates on a 256-units-per-em grid.
- ``<svg xmlns=… width=W height=H viewBox="0 0 W H"><path d="…"/></svg>\\n``:
  fixed attribute order, no timestamps, byte-stable across runs.
- Missing glyphs: a cmap test before shaping and a ``gid 0`` check after. The
  accented line falls back to the basic line, then to the name only; failing
  that, no specimen (the font is flagged ``specimen_failed``).
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class Specimen:
    svg: bytes
    line: Literal["accented", "basic", "name"]  # what line 2 shows ("name": no line 2)
    width: int
    height: int


class RelPathPen:
    """A fontTools-style pen writing a compact relative SVG path on the integer grid."""

    def __init__(self, scale: float) -> None:
        raise NotImplementedError("M2 step 5")

    def move_to(self, x: float, y: float) -> None:
        raise NotImplementedError("M2 step 5")

    def line_to(self, x: float, y: float) -> None:
        raise NotImplementedError("M2 step 5")

    def quadratic_to(self, x1: float, y1: float, x: float, y: float) -> None:
        raise NotImplementedError("M2 step 5")

    def cubic_to(self, x1: float, y1: float, x2: float, y2: float, x: float, y: float) -> None:
        raise NotImplementedError("M2 step 5")

    def close_path(self) -> None:
        raise NotImplementedError("M2 step 5")

    def path(self) -> str:
        raise NotImplementedError("M2 step 5")


def variation(axes: Mapping[str, tuple[float, float, float]]) -> dict[str, float]:
    """The instance to draw: {"wght": 400.0} when allowed, else {} (the default)."""
    raise NotImplementedError("M2 step 5")


def missing(cmap: Mapping[int, object] | set[int], text: str) -> set[str]:
    """Characters of ``text`` (ignoring spaces) the font's cmap lacks."""
    raise NotImplementedError("M2 step 5")


def render(
    font: bytes, family: str, sample: str, basic: str, *, name_only: bool = False
) -> Specimen | None:
    """Render the family name and the best sample line; None when even the name fails."""
    raise NotImplementedError("M2 step 5")
