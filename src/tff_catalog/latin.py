"""Stage "latin": the Latin gate (milestone-1 step 5, decision D4). Owner: agent P2a.

- Google families: rule A, the strict metadata test (primary script Latin or
  unset, and a ``latin`` subset), plus the dual-script families the owner
  approved (gate L, ``reviews.gate_dir(paths, "L")``).
- Other fonts: the glyph test against ``data/glyphsets/GF_Latin_{Kernel,Core}.nam``
  with the thresholds in ``ranking.toml [latin]`` (gate L1).
- Coverage is ``basic`` (the "limited accents" badge) or ``extended``.

Writes ``build/stage/latin.json`` ({id: LatinResult}) and
``build/review/latin-allowlist.md`` (the dual-script sheet, sorted by Google year
views; ``build/review/`` is gitignored, because ruling T2 keeps view counts
private).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from tff_catalog.config_model import Latin
    from tff_catalog.records import UniverseRecord
    from tff_catalog.stages import StageContext
    from tff_catalog.universe import Universe

Basis = Literal["gf_metadata", "owner_allowlist", "glyph_test"]


@dataclass(frozen=True, slots=True)
class LatinResult:
    latin: bool
    basis: Basis | None  # how it passed; None when it failed
    coverage: Literal["basic", "extended"] | None
    reason: str | None = None  # why it failed ("cjk", "kernel_missing", "share", ...)
    kernel_missing: tuple[int, ...] = ()
    core_missing: tuple[int, ...] = ()
    latin_share: float | None = None
    cjk_codepoints: int = 0


def rule_a(rec: UniverseRecord) -> bool:
    """Google's strict metadata test: primary script Latin or unset, and a ``latin`` subset."""
    raise NotImplementedError("M1 step 5")


def load_glyphset(path: Path) -> frozenset[int]:
    """Code points of a GF glyphset ``.nam`` file."""
    raise NotImplementedError("M1 step 5")


def glyph_test(cmap: set[int] | frozenset[int], th: Latin) -> LatinResult:
    """Test a font's code points against GF_Latin_Kernel and GF_Latin_Core."""
    raise NotImplementedError("M1 step 5")


def allowlist_sheet(u: Universe) -> str:
    """The dual-script review sheet for the owner (Markdown), about 30 rows."""
    raise NotImplementedError("M1 step 5")


def run(ctx: StageContext) -> None:
    """Stage "latin"."""
    raise NotImplementedError("M1 step 5")
