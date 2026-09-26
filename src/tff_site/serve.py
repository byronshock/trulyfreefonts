"""``tff-site serve``: a local preview server that sends the production headers.

It reads the header lines of the ``(tff_security)`` and ``(tff_site)`` snippets in
``ops/caddy/site.caddy``, so the preview, CI, staging and production share one source:

- every response gets the ``tff_security`` headers, and no ``Server`` header;
- ``/assets/*`` gets ``Cache-Control: public, max-age=31536000, immutable``;
- everything else gets ``Cache-Control: no-cache, no-transform``;
- a missing file is answered with ``/404.html`` and status 404, with the same headers.

It serves ``index.html`` for directory paths and never compresses (CI uses real Caddy for
the compressed performance runs). Standard library only.
"""

from dataclasses import dataclass
from http.server import ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_CADDY = REPO_ROOT / "ops" / "caddy" / "site.caddy"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


@dataclass(frozen=True, slots=True)
class CaddyHeaders:
    """Headers parsed from site.caddy: ``security`` for every response, then per route kind."""

    security: dict[str, str]
    remove: tuple[str, ...]
    immutable: dict[str, str]
    revalidate: dict[str, str]


def parse_headers(snippet: str) -> CaddyHeaders:
    """Parse the header lines of the ``tff_security`` and ``tff_site`` snippets.

    A field name may start with ``>`` (Caddy's deferred header, used for the
    ``@revalidate`` Cache-Control so that ``encode`` still compresses HTML); the
    parser strips it. A leading ``-`` removes a header (``-Server``).
    """
    raise NotImplementedError("M2 step 1")


def make_server(
    site_dir: Path,
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    snippet: Path = SITE_CADDY,
) -> ThreadingHTTPServer:
    """Return a bound, not yet started server for ``site_dir``; port 0 picks a free port."""
    raise NotImplementedError("M2 step 1")


def serve(
    site_dir: Path,
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    snippet: Path = SITE_CADDY,
) -> None:
    """Serve ``site_dir`` until interrupted."""
    raise NotImplementedError("M2 step 1")
