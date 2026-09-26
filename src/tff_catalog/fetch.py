"""The shared HTTP fetcher and the "fetch" stage (milestone-1 step 3). Owner: agent I1.

Every network read goes through ``Fetcher`` (ruff bans ``urllib.request`` and
``requests`` elsewhere). It:

- sends ``USER_AGENT``, never a personal email;
- keeps a per-host minimum interval (default 1 request a second);
- retries with exponential backoff on connection errors, 429 and 5xx,
  honouring ``Retry-After``;
- makes conditional GETs from a previous manifest entry (ETag,
  Last-Modified) and reports ``not_modified``;
- refuses any host outside the set it was scoped to (``HostNotAllowed``),
  so a collector can only reach its declared ``hosts``;
- charges named per-run ``Budget``s (the GitHub API budget);
- accepts an ``httpx`` transport, so tests use ``httpx.MockTransport``.

Stage "fetch" (``run``) runs each enabled collector's ``fetch()`` into a new
snapshot, skipping sources whose snapshot for the run date is already complete
unless ``--refetch``.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tff_catalog import __version__

if TYPE_CHECKING:
    import logging

    import httpx

    from tff_catalog.stages import StageContext
    from tff_catalog.store import FetchRecord

USER_AGENT = f"trulyfreefonts-catalog/{__version__} (+https://github.com/byronshock/trulyfreefonts)"
DEFAULT_MIN_INTERVAL = 1.0  # seconds between requests to one host
DEFAULT_RETRIES = 4
DEFAULT_TIMEOUT = 60.0


class HostNotAllowed(RuntimeError):
    """A request went to a host the fetcher was not scoped to."""


class BudgetExceeded(RuntimeError):
    """A named per-run request budget ran out."""


class FetchError(RuntimeError):
    """A request failed after every retry, or returned an unexpected status."""


@dataclass(frozen=True, slots=True)
class FetchResult:
    """One completed request."""

    url: str  # the requested URL
    final_url: str  # after redirects
    status: int
    headers: tuple[tuple[str, str], ...]  # lower-cased names, in response order
    content: bytes  # empty when streamed to ``path`` or when not modified
    path: Path | None  # set when the body was streamed to a file
    sha256: str  # of the body ("" when not modified)
    size: int  # body length in bytes
    fetched_at: datetime  # aware UTC, from clock.utc_now()
    etag: str | None = None
    last_modified: str | None = None
    not_modified: bool = False

    def text(self) -> str:
        """The body decoded as UTF-8."""
        raise NotImplementedError("M1 step 3")

    def json(self) -> Any:
        """The body parsed as JSON, after stripping an optional ``)]}'`` XSSI prefix."""
        raise NotImplementedError("M1 step 3")

    def to_record(self, *, kept: bool = False) -> FetchRecord:
        """The manifest entry for this request (``store.FetchRecord``)."""
        raise NotImplementedError("M1 step 3")


@dataclass(slots=True)
class Budget:
    """A named per-run request budget, for example ``Budget("github", 900)``."""

    name: str
    limit: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return self.limit - self.used

    def spend(self, n: int = 1) -> None:
        """Charge ``n`` requests; raise ``BudgetExceeded`` past the limit."""
        raise NotImplementedError("M1 step 3")


class Fetcher:
    """Rate-limited, retrying HTTP client shared by every collector in a run."""

    def __init__(
        self,
        *,
        hosts: Iterable[str] | None = None,
        user_agent: str = USER_AGENT,
        min_interval: Mapping[str, float] | None = None,
        retries: int = DEFAULT_RETRIES,
        timeout: float = DEFAULT_TIMEOUT,
        budgets: Iterable[Budget] = (),
        transport: httpx.BaseTransport | None = None,
        log: logging.Logger | None = None,
    ) -> None:
        """Create a fetcher. ``hosts=None`` allows any host (use ``scoped`` per collector)."""
        raise NotImplementedError("M1 step 3")

    def scoped(self, hosts: Iterable[str]) -> Fetcher:
        """A view sharing this fetcher's client, rate state and budgets, limited to ``hosts``."""
        raise NotImplementedError("M1 step 3")

    def get(
        self,
        url: str,
        *,
        params: Mapping[str, str | int] | None = None,
        headers: Mapping[str, str] | None = None,
        previous: FetchRecord | None = None,
        to: Path | None = None,
        budget: str | None = None,
        expect: Iterable[int] = (200,),
    ) -> FetchResult:
        """GET ``url``; conditional when ``previous`` is given; streamed to ``to`` when set."""
        raise NotImplementedError("M1 step 3")

    def get_range(
        self, url: str, start: int, end: int, *, budget: str | None = None
    ) -> FetchResult:
        """GET bytes ``start..end`` (inclusive) with an HTTP Range header (font tables)."""
        raise NotImplementedError("M1 step 3")

    def head(self, url: str, *, headers: Mapping[str, str] | None = None) -> FetchResult:
        """HEAD ``url``, following redirects (link checks, foundry URLs)."""
        raise NotImplementedError("M1 step 3")

    def post_json(
        self,
        url: str,
        payload: object,
        *,
        headers: Mapping[str, str] | None = None,
        budget: str | None = None,
    ) -> FetchResult:
        """POST a JSON body (ecosyste.ms bulk lookup)."""
        raise NotImplementedError("M1 step 3")

    def graphql(self, query: str, variables: Mapping[str, object] | None = None) -> dict[str, Any]:
        """Run a GitHub GraphQL query with ``GITHUB_TOKEN``; charges the ``github`` budget."""
        raise NotImplementedError("M1 step 3")

    def close(self) -> None:
        raise NotImplementedError("M1 step 3")

    def __enter__(self) -> Fetcher:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def run(ctx: StageContext) -> None:
    """Stage "fetch": snapshot every enabled collector (``--only`` narrows the list).

    For each collector: skip when ``<store>/<name>/<run_date>/`` is complete
    (unless ``--refetch``, which is refused for dates in ``state/run_history.json``);
    otherwise open a ``SnapshotWriter``, build a ``FetchContext`` with a scoped
    fetcher, call ``fetch()``, and close the writer. A failing collector is
    logged and left to the stale policy; the stage fails only if every one fails.
    """
    raise NotImplementedError("M1 step 3")
