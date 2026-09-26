"""Stage "parse" (design-m1 §1.2 row 2). Owner: the lead, with the collector framework (step 3).

For every enabled collector, pick the snapshot this run uses (today's, or the
latest complete one within the stale window), run ``parse()`` offline and write
``build/stage/records/<source>.jsonl`` in canonical order. Collectors with
``needs_baseline`` are also parsed on their baseline snapshots (named in
``state/run_history.json``) into ``<source>@<baseline-date>.jsonl``.
``build/stage/stale.json`` lists every source used stale, with its data date.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import logging

    from tff_catalog.collectors.base import Collector
    from tff_catalog.records import Record
    from tff_catalog.stages import StageContext
    from tff_catalog.store import Snapshot


def parse_source(
    c: Collector, snap: Snapshot, settings: object, log: logging.Logger
) -> list[Record]:
    """Run ``c.parse`` on ``snap`` and return the records sorted by ``records.sort_key``.

    Raises ``TypeError`` for a record type outside ``c.emits`` and ``ValueError``
    for a namespace outside ``records.NAMESPACES``.
    """
    raise NotImplementedError("M1 step 3")


def baselines(ctx: StageContext, c: Collector) -> list[Snapshot]:
    """The earlier snapshots a lifetime-counter collector needs (run_history pointers)."""
    raise NotImplementedError("M1 step 3")


def run(ctx: StageContext) -> None:
    """Stage "parse": write ``stage/records/*.jsonl`` and ``stage/stale.json``."""
    raise NotImplementedError("M1 step 3")
