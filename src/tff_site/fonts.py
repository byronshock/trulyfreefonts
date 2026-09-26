"""``tff-site fetch-fonts``: download the font files "Type your own text" serves.

For every font with ``preview_ok`` and a ``font_file``, it downloads ``font_file.url`` into
the cache as ``<cache>/<sha256>`` (the file name is the expected hash), checks the sha256 and
size, and skips files already cached. A mismatch is an error and nothing is kept. The files
are served unchanged (D3) and never committed. ``tff-site build`` reads only the cache.
"""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CACHE = Path.home() / ".cache" / "tff" / "fonts"


@dataclass(frozen=True, slots=True)
class FetchReport:
    """Font ids fetched now, already cached, and failed (with the reason)."""

    fetched: list[str] = field(default_factory=list)
    cached: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)


def cache_path(sha256: str, cache_dir: Path = DEFAULT_CACHE) -> Path:
    """Return where the file with this sha256 lives in the cache."""
    return cache_dir / sha256


def file_sha256(path: Path) -> str:
    """Return the hex sha256 of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_fonts(data_path: Path, cache_dir: Path = DEFAULT_CACHE) -> FetchReport:
    """Fill the cache with every ``font_file`` the catalog at ``data_path`` names."""
    raise NotImplementedError("M2 step 5")
