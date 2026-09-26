"""Build the static site from ``catalog-site.json`` into a directory.

The build is offline and deterministic: it makes no network request (tests run it under a
socket guard), reads no clock, and two builds of the same inputs are byte-identical.

Steps: validate the data (``tff_site.data``); concatenate and hash the JS and CSS parts
(``tff_site.assets``); write the list-index and details JSON; copy each ``preview`` SVG from
``specimens/`` next to the data file to ``/assets/specimens/<id>.<h>.svg``, checking its
sha256; copy each ``font_file`` from the font cache to ``/assets/fonts/<id>.<h>.<ext>``;
render the templates (``site/templates``, Jinja2 with autoescape and StrictUndefined) and the
pages (``tff_site.pages``); write ``robots.txt``, ``sitemap.xml``, the static files and
``version.txt``. Output layout: site/CONTRACT.md, "Build output".
"""

from dataclasses import dataclass
from pathlib import Path

from tff_site import fonts

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_DIR = REPO_ROOT / "site"
DEFAULT_DATA = REPO_ROOT / "build" / "catalog-site.json"
DEFAULT_OUT = REPO_ROOT / "build" / "site"


@dataclass(frozen=True, slots=True)
class BuildResult:
    """What a build wrote. ``version`` holds the ``version.txt`` fields."""

    out_dir: Path
    files: int
    version: dict[str, str]


def build(
    data_path: Path = DEFAULT_DATA,
    out_dir: Path = DEFAULT_OUT,
    *,
    fonts_dir: Path = fonts.DEFAULT_CACHE,
    commit: str | None = None,
    allow_dirty: bool = False,
    font_files: bool = True,
    site_dir: Path = SITE_DIR,
) -> BuildResult:
    """Build the site into ``out_dir``, replacing its contents.

    ``commit`` defaults to ``git rev-parse HEAD`` of the repository; a dirty tree is refused
    unless ``allow_dirty``, which records ``<sha>-dirty``. With ``font_files=False`` no font
    file is copied and "Type your own text" is left out (for builds without the font cache).
    A missing or mismatching specimen or font file is an error, except a preview whose sha256
    is ``data.PLACEHOLDER_SHA256``, which is built as "Preview not available yet".
    """
    raise NotImplementedError("M2 step 1")


def git_commit(repo_root: Path = REPO_ROOT, *, allow_dirty: bool = False) -> str:
    """Return the 40-hex HEAD commit, with ``-dirty`` appended when allowed and dirty."""
    raise NotImplementedError("M2 step 1")


def version_txt(commit: str, doc: dict) -> str:
    """Return ``version.txt``: commit, run_date, method_version, catalog_sha256, schema.

    It never contains a build time, so rebuilding the same commit gives the same bytes.
    """
    raise NotImplementedError("M2 step 1")
