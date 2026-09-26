"""The "specimens" stage (design-m2 §3). Owner: agent A5.

1. For each ``preview_ok`` font, fetch ``font_file.url`` with the M1 fetcher
   into ``~/.cache/tff/fonts/<sha256>``.
2. Verify the sha256; a mismatch sets ``specimen_hash_mismatch`` and gives no image.
3. Render ``build/specimens/<id>.svg``.
4. Record ``preview {path, sha256}``.

The cache key is sha256(font) + sample + renderer version + uharfbuzz version,
so unchanged inputs skip rendering and a refresh only touches changed fonts.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tff_catalog import stageio

if TYPE_CHECKING:
    from tff_catalog.fetch import Fetcher
    from tff_catalog.stages import StageContext

FONT_CACHE = Path("~/.cache/tff/fonts")


@dataclass(frozen=True, slots=True)
class Preview:
    """One font's specimen, ``build/stage/previews.json`` ({id: Preview})."""

    path: str | None  # "specimens/<id>.svg", None when there is no image
    sha256: str | None
    flags: tuple[str, ...] = ()  # specimen_failed, specimen_name_only, specimen_hash_mismatch


def cache_key(font_sha256: str, sample: str, renderer_version: int, hb_version: str) -> str:
    """The render-cache key (hex sha256 of the joined inputs)."""
    raise NotImplementedError("M2 step 5")


def fetch_font(url: str, sha256: str, fetcher: Fetcher | None, cache_dir: Path) -> Path | None:
    """The cached font file, fetched if needed; None on a hash mismatch."""
    raise NotImplementedError("M2 step 5")


def run(ctx: StageContext) -> None:
    """Stage "specimens": render every preview and write ``build/stage/previews.json``.

    Until M2 step 5 replaces it, this is a logged no-op that writes an empty
    ``previews.json``, so ``preview`` stays null and ``refresh`` (M1 step 18)
    does not depend on Milestone 2 (design-m1 §1.2 row 15b: "default no-op").
    """
    ctx.log.info("specimens: not built until M2 step 5; every preview stays null")
    stageio.dump_stage(ctx.paths, "previews", {})
