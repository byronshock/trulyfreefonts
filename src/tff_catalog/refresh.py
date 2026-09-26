"""The one-command refresh (milestone-1 step 18). Owner: agent P13.

Runs ``stages.pipeline()`` in order (fetch is skipped in replay), reruns
"rank" and "membership" once when "verify" adds exclusions, writes
``$TFF_STORE/_runs/<date>.json``, and leaves ``build/`` ready for the refresh
pull request (``build/state/`` included). It never writes ``state/``.

``build/state/``: refresh empties it before the first stage, writes its own
part (``run_history``, ``state.write_part``), and finishes with
``state.complete_next_state``, so the directory always holds every state file.

``--from-snapshots D`` replays from the store with the network off: a clean
clone given the same snapshots produces identical ``build/`` output.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tff_catalog.paths import Paths
    from tff_catalog.stages import RunOptions


@dataclass(frozen=True, slots=True)
class RunResult:
    run_date: date
    build: Path
    stages: tuple[str, ...]  # stages run, in order (a rerun appears twice)
    stale: tuple[str, ...]  # sources used stale
    failures: tuple[str, ...]  # hard-check failures
    seconds: float

    @property
    def ok(self) -> bool:
        return not self.failures


def refresh(
    paths: Paths,
    run_date: date,
    from_snapshots: date | None = None,
    *,
    options: RunOptions | None = None,
) -> RunResult:
    """Run the whole pipeline for ``run_date``."""
    raise NotImplementedError("M1 step 18")
