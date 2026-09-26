"""Git sources: sparse and blobless clones, deleted paths, file history. Owner: agent I1.

Collectors that read git repositories (google/fonts, fontsource, fontist) and
the alias miners use these helpers instead of calling git directly. Clones go
into the run's ``RawDir`` and are deleted after the run.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DeletedPath:
    """A path removed by a commit (``git log --diff-filter=D``)."""

    commit: str
    day: date  # committer date, UTC
    path: str


def sparse_clone(
    url: str,
    dest: Path,
    patterns: Sequence[str],
    *,
    ref: str | None = None,
    depth: int | None = 1,
) -> str:
    """Clone ``url`` into ``dest`` with only ``patterns`` checked out; return the commit sha.

    Uses ``--filter=blob:none --sparse`` and non-cone patterns, so for example
    google/fonts' ``/ofl/*/METADATA.pb`` costs about 4 MB.
    """
    raise NotImplementedError("M1 step 3")


def blobless_clone(url: str, dest: Path, *, ref: str | None = None, bare: bool = True) -> str:
    """Clone full history without blobs (``--filter=blob:none``); return the commit sha."""
    raise NotImplementedError("M1 step 3")


def log_deleted(
    repo: Path, paths: Sequence[str] = (), *, since: date | None = None
) -> list[DeletedPath]:
    """List paths deleted in ``repo``'s history, oldest first; ``--no-renames``."""
    raise NotImplementedError("M1 step 3")


def show(repo: Path, rev: str, path: str) -> bytes:
    """Return the bytes of ``path`` at ``rev`` (``git show <rev>:<path>``)."""
    raise NotImplementedError("M1 step 3")


def head_sha(repo: Path) -> str:
    """Return the commit sha checked out in ``repo``."""
    raise NotImplementedError("M1 step 3")
