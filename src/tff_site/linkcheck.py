"""``tff-site linkcheck``: check that license texts and download links answer HTTP 200.

It visits each chosen font's ``license.text_url``, ``links.primary`` and ``links.designer``,
at most ``rate`` requests a second per host, following redirects. This is the Milestone 2
step 4 check for the owner's ten fonts; Milestone 1 step 14 checks every link monthly.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class LinkResult:
    """One checked link: the font, which field, the URL and the final HTTP status (0: failed)."""

    font_id: str
    field: str
    url: str
    status: int


def linkcheck(
    data_path: Path, *, ids: Iterable[str] | None = None, rate: float = 1.0
) -> list[LinkResult]:
    """Check the links of the fonts in ``ids`` (default: every font) and return the results."""
    raise NotImplementedError("M2 step 4")
