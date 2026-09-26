"""Stage "match": the Milestone 3 slot (M3 step 3). Owner: Milestone 3.

Milestone 3 writes ``build/match-site.json`` here, from the universe, the
aliases and ``build/names.json``, for on-device owned-font matching. It runs in
``refresh`` after "export-site", so the monthly refresh pull request
regenerates the file (M3 step 12). Until then ``run`` is a logged no-op and
writes nothing.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tff_catalog.stages import StageContext


def run(ctx: StageContext) -> None:
    """Stage "match": a no-op until Milestone 3 step 3."""
    ctx.log.info("match: not built until M3 step 3; build/match-site.json is not written")
