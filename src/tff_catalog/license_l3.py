"""Stage "verify": L3 license verification for catalog candidates (milestone-1 step 6b). Owner: agent P9.

For the overall top 700 and the top 150 of the project and both desktop views:
fetch the upstream license text, match its fingerprint against
``data/license-texts/<SPDX>.txt``, check name-table IDs 13 and 14, and record
text_url, sha256, checked_on, font_version and ``font_file`` {url, sha256}
(Milestone 2 builds previews from that file). Texts and font reads go through
the ``license_texts`` and ``font_facts`` pseudo-sources, so replay is offline.

A changed text hash puts the font back in the queue. A new exclusion makes
refresh rerun "rank" and "membership" once.

Writes ``build/stage/l3.json``, ``build/stage/queues/l3.json`` and
``build/state/license_hashes.json``.
"""

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Literal

from tff_catalog.records import FontFileRef

if TYPE_CHECKING:
    from tff_catalog.stages import StageContext
    from tff_catalog.universe import Family


@dataclass(frozen=True, slots=True)
class L3Result:
    family_id: str
    level: Literal["L3", "failed", "ruling"]
    checked_on: date
    text_url: str | None
    text_sha256: str | None
    matched: str | None  # SPDX id whose canonical text matched
    name_ids: tuple[str | None, str | None]  # name table IDs 13 and 14
    font_version: str | None
    font_file: FontFileRef | None
    problems: tuple[str, ...] = ()


def fingerprint(text: str) -> str:
    """A whitespace-, case- and punctuation-insensitive sha256 of a license text.

    Copyright lines and the Reserved Font Name clause are removed first, so
    every OFL-1.1 text of any family gives the same fingerprint.
    """
    raise NotImplementedError("M1 step 6b")


def verify(fam: Family, ctx: StageContext) -> L3Result:
    """Run L3 for one family."""
    raise NotImplementedError("M1 step 6b")


def run(ctx: StageContext) -> None:
    """Stage "verify"."""
    raise NotImplementedError("M1 step 6b")


def cmd_check(ctx: StageContext) -> int:
    """``verify --check``: non-zero unless every catalog font is L3 or has an owner ruling."""
    raise NotImplementedError("M1 step 6b")
