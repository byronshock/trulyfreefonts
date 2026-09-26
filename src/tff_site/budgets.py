"""``tff-site check``: size budgets and a CSP lint of a built site.

Sizes are gzip level 9 (``gzip_size``), in decimal kilobytes:

- the list page's HTML + CSS + JS: at most ``PAGE_MAX``;
- the list index: at most ``LIST_INDEX_MAX``;
- the details payload: at most ``DETAILS_MAX`` (loaded lazily; shard it if over);
- specimens: at least half at most ``SPECIMEN_HALF_MAX``, none over ``SPECIMEN_MAX``,
  all together under ``SPECIMENS_TOTAL_RAW_MAX`` uncompressed.

The CSP lint fails on an inline ``<script>`` without ``src``, a ``<style>`` element, any
``style=`` or ``on*=`` attribute, a ``<form>``, and ``rel=prefetch``.
"""

import gzip
from dataclasses import dataclass
from pathlib import Path

KB = 1000
PAGE_MAX = 100 * KB
LIST_INDEX_MAX = 100 * KB
DETAILS_MAX = 150 * KB
SPECIMEN_HALF_MAX = 5 * KB
SPECIMEN_MAX = 30 * KB
SPECIMENS_TOTAL_RAW_MAX = 10_000 * KB


@dataclass(frozen=True, slots=True)
class Problem:
    """One failed check: the file (relative to the site root) and what is wrong."""

    path: str
    message: str


def gzip_size(data: bytes) -> int:
    """Return the size of ``data`` compressed with gzip level 9 (fixed mtime)."""
    return len(gzip.compress(data, compresslevel=9, mtime=0))


def check(site_dir: Path) -> list[Problem]:
    """Run every budget and the CSP lint on a built site; an empty list means it passes."""
    raise NotImplementedError("M2 step 10")


def lint_html(path: str, html: str) -> list[Problem]:
    """Return CSP-lint problems in one HTML file."""
    raise NotImplementedError("M2 step 10")
