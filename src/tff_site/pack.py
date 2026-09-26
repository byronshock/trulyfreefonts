"""``tff-site pack``: a deterministic tar of a built site, and its manifest.

The manifest, ``site.manifest.json``, is ``{"commit": <sha40>, "files": {<path>: {"sha256",
"size"}}}`` with paths relative to the site root, sorted. The server's ``tff-receive plan``
reads it and answers with the paths it lacks; ``pack --only`` then sends just those.

The tar holds regular files and directories only, sorted by path, with mtime 0, uid/gid 0,
empty owner names and mode 0644 (0755 for directories), so the same site gives the same bytes.
Paths must match ``^([a-z0-9][a-z0-9._-]*/)*[a-z0-9][a-z0-9._-]*$`` (the receiver's rule).
"""

from collections.abc import Iterable
from pathlib import Path
from typing import Any, BinaryIO


def manifest(site_dir: Path, *, commit: str | None = None) -> dict[str, Any]:
    """Return the manifest of ``site_dir`` (``commit`` as in ``pack``)."""
    raise NotImplementedError("M2 step 11")


def pack(
    site_dir: Path,
    out: BinaryIO,
    *,
    commit: str | None = None,
    only: Iterable[str] | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Write the tar of ``site_dir`` (or just the paths in ``only``) to ``out``.

    ``commit`` defaults to the ``commit=`` line of ``site_dir/version.txt``. Writes the
    manifest to ``manifest_path`` when given, and returns it.
    """
    raise NotImplementedError("M2 step 11")
