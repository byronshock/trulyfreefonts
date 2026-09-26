"""Stage "links": official download links (milestone-1 step 14). Owner: agent P11.

- Google families: primary is the specimen page; designer is ``minisite_url``
  or ``repository_url``, never googlefontdirectory-hg.
- Others: the designer's homepage or the repository's releases page; never a
  release asset, ``/releases/latest`` or an aggregator; auto-accepted only
  when two sources agree.
- Owner-approved overrides come from gate K (``reviews.gate_dir(paths, "K")``).

A monthly check records every response in the ``link_checks`` pseudo-source,
so replay is offline. Writes ``build/stage/links.json``.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tff_catalog.records import UniverseRecord
    from tff_catalog.stages import StageContext
    from tff_catalog.universe import Family


@dataclass(frozen=True, slots=True)
class Link:
    url: str  # https
    label: str | None = None


@dataclass(frozen=True, slots=True)
class Links:
    primary: Link
    designer: Link | None
    basis: str  # "google_specimen", "override", "two_sources", ...


@dataclass(frozen=True, slots=True)
class LinkCheck:
    url: str
    status: int
    final_url: str
    problems: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == 200 and not self.problems


def policy_problems(url: str) -> list[str]:
    """Why ``url`` breaks the link policy (not https, release asset, /releases/latest, hg mirror, aggregator)."""
    raise NotImplementedError("M1 step 14")


def choose(fam: Family, recs: Iterable[UniverseRecord], overrides: Mapping[str, Links]) -> Links:
    """Pick one family's links."""
    raise NotImplementedError("M1 step 14")


def check(links: Mapping[str, Links], ctx: StageContext) -> dict[str, LinkCheck]:
    """HEAD-check every primary and designer link (through the store in replay)."""
    raise NotImplementedError("M1 step 14")


def run(ctx: StageContext) -> None:
    """Stage "links"."""
    raise NotImplementedError("M1 step 14")


def cmd_check(ctx: StageContext) -> int:
    """``links --check``: non-zero unless every primary link is compliant and returns 200."""
    raise NotImplementedError("M1 step 14")
