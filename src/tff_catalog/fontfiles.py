"""Font-file facts read from the files themselves (milestone-1 steps 5 and 5b). Owner: agent P2b.

``read_tables`` fetches only the tables it needs with HTTP Range requests (the
table directory first), so a 1 MB font costs a few kilobytes. Results are
cached in ``$TFF_STORE/_cache/fontfacts.jsonl``, keyed by the file's sha256 and,
for google/fonts files, the git blob sha1, so later runs fetch only changed
files. Every read in a live run is also recorded in the ``font_facts``
pseudo-source, so a replay needs no network.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from tff_catalog.fetch import Fetcher
    from tff_catalog.records import FontFileRef

TABLES = ("head", "name", "cmap", "post", "OS/2", "fvar")


@dataclass(frozen=True, slots=True)
class FontFacts:
    sha256: str
    git_blob: str | None
    format: Literal["ttf", "otf", "woff", "woff2"]
    cmap: tuple[tuple[int, int], ...]  # code point ranges (first, last), sorted
    family_name: str | None  # name ID 16, else 1
    full_name: str | None  # name ID 4
    postscript_name: str | None  # name ID 6
    version: str | None  # name ID 5
    license_description: str | None  # name ID 13
    license_url: str | None  # name ID 14
    is_fixed_pitch: bool | None  # post.isFixedPitch
    panose_proportion: int | None  # OS/2 panose bProportion (9 = monospaced)
    axes: tuple[tuple[str, float, float, float], ...] = ()  # (tag, min, default, max)

    def codepoints(self) -> frozenset[int]:
        raise NotImplementedError("M1 step 5b")

    def to_json(self) -> dict[str, Any]:
        raise NotImplementedError("M1 step 5b")

    @classmethod
    def from_json(cls, d: dict[str, Any]) -> FontFacts:
        raise NotImplementedError("M1 step 5b")


class FontFileCache:
    """The append-only facts cache at ``$TFF_STORE/_cache/fontfacts.jsonl``."""

    def __init__(self, path: Path) -> None:
        raise NotImplementedError("M1 step 5b")

    def get(self, *, sha256: str | None = None, git_blob: str | None = None) -> FontFacts | None:
        raise NotImplementedError("M1 step 5b")

    def put(self, facts: FontFacts) -> None:
        raise NotImplementedError("M1 step 5b")

    def flush(self) -> None:
        """Append new entries, sorted, in one atomic write."""
        raise NotImplementedError("M1 step 5b")


def read_tables(url: str, tags: Sequence[str], fetcher: Fetcher) -> dict[str, bytes]:
    """Fetch the named sfnt tables of the font at ``url`` with HTTP Range requests.

    Falls back to one full GET when the server ignores Range or the file is
    WOFF2 (whose tables are compressed together).
    """
    raise NotImplementedError("M1 step 5b")


def facts_from_bytes(data: bytes, *, git_blob: str | None = None) -> FontFacts:
    """Read facts from a whole font file with fontTools."""
    raise NotImplementedError("M1 step 5b")


def facts_for(ref: FontFileRef, fetcher: Fetcher | None, cache: FontFileCache) -> FontFacts:
    """Facts for one file: from the cache, else fetched (never in replay)."""
    raise NotImplementedError("M1 step 5b")
