"""Stage "facts": category, monospace and formats (milestone-1 step 5b). Owner: agent P2b.

Sources in order: Google metadata, Fontsource, then the font's own tables
(``fontfiles``), cached by file hash. Every family gets all three facts.
Writes ``build/stage/facts.json`` ({id: Facts}).
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from tff_catalog.fontfiles import FontFacts
    from tff_catalog.records import UniverseRecord
    from tff_catalog.stages import StageContext
    from tff_catalog.universe import Universe

# The catalog-site vocabulary (schemas/catalog-site.schema.json).
Category = Literal["sans-serif", "serif", "display", "handwriting", "monospace"]


@dataclass(frozen=True, slots=True)
class Facts:
    category: Category
    is_monospace: bool
    variable: bool
    static: bool
    basis: str  # which source decided: "google_metadata", "fontsource", "font_file", ...


def normalise_category(raw: str, source: str) -> Category | None:
    """Map a source's category word ("Sans Serif", "sans-serif", "mono") to ``Category``."""
    raise NotImplementedError("M1 step 5b")


def derive_facts(
    u: Universe, recs: Iterable[UniverseRecord], font_facts: Mapping[str, FontFacts]
) -> dict[str, Facts]:
    """Facts for every eligible family; ``font_facts`` is keyed by file sha256."""
    raise NotImplementedError("M1 step 5b")


def run(ctx: StageContext) -> None:
    """Stage "facts"."""
    raise NotImplementedError("M1 step 5b")
