"""The specimen budget (design-m2 §3). Owner: agent A5.

At least half the files at or under 5 KB gzip -9, none over 30 KB (those are
re-rendered with the name only and flagged ``specimen_name_only``), and under
10 MB in total. Projected: about 4.5 MB raw, 1.5 MB gzip.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tff_catalog.stages import StageContext


@dataclass(frozen=True, slots=True)
class BudgetReport:
    files: int
    small_share: float  # share of files at or under SMALL_GZIP_BYTES gzipped
    over_limit: tuple[str, ...]  # file names over MAX_FILE_BYTES
    total_bytes: int

    @property
    def ok(self) -> bool:
        raise NotImplementedError("M2 step 5")


def check(directory: Path) -> BudgetReport:
    """Measure every ``*.svg`` in ``directory``."""
    raise NotImplementedError("M2 step 5")


def cmd_check(ctx: StageContext) -> int:
    """``tff-catalog specimens --check``: non-zero when the budget fails."""
    raise NotImplementedError("M2 step 5")
