"""The snapshot store (design-m1 §4, decision D15). Owner: agent I2.

Layout under ``$TFF_STORE`` (a clone of the private data repository)::

    <source>/<YYYY-MM-DD>/manifest.json + extracts (*.json, *.jsonl.gz, *.csv.gz)
    license_texts/<date>/  font_facts/<date>/  link_checks/<date>/   pseudo-sources for replay
    _cache/fontfacts.jsonl      keyed by file sha256 (+ git blob sha1); append-only
    _runs/<YYYY-MM-DD>.json     run manifest: code commit, config hash, snapshot per source, stale flags, sizes
    _fixtures/<collector>/      real fixtures kept private (tests marked `store`)
    _seed/                      one-off copies (old library scratchpad, probes)

Rules:
- One snapshot per (source, date). ``SnapshotWriter`` builds ``<date>.tmp/``
  and renames it atomically; a complete snapshot is never rewritten except by
  ``--refetch``, which is refused for dates in ``state/run_history.json``.
- Extracts over ``GZIP_OVER_BYTES`` are gzipped (``mtime=0``).
- ``check()`` fails over the size limits below and warns past ``REPO_WARN_BYTES``.
- Big raw downloads go in a ``RawDir`` under ``$TFF_RAW/<run_id>/``, deleted
  when the run ends unless ``--keep-raw``.
- Only ``commit()`` (the refresh workflow, or ``tff-catalog store commit``)
  pushes, and never when ``TFF_STORE_PUSH=0``.

Manifest (``manifest.json``, ``schema: 1``; ``schemas/stage/manifest.schema.json``)::

    {"schema":1,"source":"homebrew_analytics","date":"2026-10-03","collector_version":1,
     "complete":true,"data_date":"2026-10-02","window":{"start":"2025-10-03","end":"2026-10-02"},
     "fetched":[{"url":…,"status":200,"fetched_at":"2026-10-03T06:17:22Z","sha256":…,
                 "bytes":1787534,"etag":…,"last_modified":…,"kept":false}],
     "extracts":[{"path":"cask-install-365d.json","sha256":…,"bytes":141233,"rows":2964}],
     "stale_of":null,"notes":[]}
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tff_catalog.paths import Paths

MANIFEST_SCHEMA = 1
MANIFEST_NAME = "manifest.json"
GZIP_OVER_BYTES = 256 * 1024
EXTRACT_MAX_BYTES = 8 * 1024 * 1024
SNAPSHOT_MAX_BYTES = 10 * 1024 * 1024
RUN_MAX_BYTES = 30 * 1024 * 1024
REPO_WARN_BYTES = 1024 * 1024 * 1024
GROWTH_FLAG = 0.20  # month-on-month growth flagged in review.md
PUSH_ENV = "TFF_STORE_PUSH"
PSEUDO_SOURCES = ("license_texts", "font_facts", "link_checks")


def stale_max_age(max_months: int) -> timedelta:
    """How old a reused snapshot may be: ``max_months`` times 31 days.

    ``max_months`` is ``ranking.toml [stale] max_months``; callers (fetch, parse,
    refresh) pass ``cfg.ranking.stale.max_months``, so the config is the one place
    the window is set.
    """
    return timedelta(days=31 * max_months)


class SnapshotExists(RuntimeError):
    """A complete snapshot already exists for this (source, date)."""


class SnapshotFrozen(RuntimeError):
    """``--refetch`` on a date that a merged run used (listed in run_history)."""


@dataclass(frozen=True, slots=True)
class FetchRecord:
    """One entry of a manifest's ``fetched`` list."""

    url: str
    status: int
    fetched_at: str  # ISO UTC, "…Z"
    sha256: str
    bytes: int
    etag: str | None = None
    last_modified: str | None = None
    kept: bool = False  # the raw body is also an extract


@dataclass(frozen=True, slots=True)
class ExtractRecord:
    """One entry of a manifest's ``extracts`` list."""

    path: str  # relative to the snapshot directory
    sha256: str
    bytes: int
    rows: int | None = None


@dataclass(frozen=True, slots=True)
class Manifest:
    schema: int
    source: str
    date: date
    collector_version: int
    complete: bool
    data_date: date | None
    window: tuple[date, date] | None  # (start, end) of the data
    fetched: tuple[FetchRecord, ...]
    extracts: tuple[ExtractRecord, ...]
    stale_of: date | None = None  # set on a stale reuse: the date it stands in for
    notes: tuple[str, ...] = ()

    def to_json(self) -> dict[str, Any]:
        raise NotImplementedError("M1 step 3")

    @classmethod
    def from_json(cls, d: dict[str, Any]) -> Manifest:
        raise NotImplementedError("M1 step 3")


@dataclass(frozen=True, slots=True)
class Snapshot:
    """A complete snapshot on disk. Read-only."""

    source: str
    date: date
    path: Path
    manifest: Manifest

    def has(self, name: str) -> bool:
        raise NotImplementedError("M1 step 3")

    def extract_path(self, name: str) -> Path:
        """Path of extract ``name``; raises ``FileNotFoundError`` if the manifest lacks it."""
        raise NotImplementedError("M1 step 3")

    def read_bytes(self, name: str) -> bytes:
        """Extract bytes, gunzipped when the name ends in ``.gz``; sha256-checked."""
        raise NotImplementedError("M1 step 3")

    def load_json(self, name: str) -> Any:
        raise NotImplementedError("M1 step 3")

    def iter_jsonl(self, name: str) -> Iterator[Any]:
        raise NotImplementedError("M1 step 3")


class SnapshotWriter:
    """Builds ``<store>/<source>/<date>.tmp/`` and publishes it atomically on ``close()``."""

    def write_bytes(self, name: str, data: bytes, *, rows: int | None = None) -> ExtractRecord:
        """Write an extract (gzipped if ``name`` ends in ``.gz``); returns its manifest entry."""
        raise NotImplementedError("M1 step 3")

    def write_json(self, name: str, obj: object) -> ExtractRecord:
        """Write an extract as canonical pretty JSON (``jsonio``)."""
        raise NotImplementedError("M1 step 3")

    def write_jsonl(self, name: str, rows: Iterable[object]) -> ExtractRecord:
        """Write an extract as JSON Lines; ``rows`` in the manifest is the line count."""
        raise NotImplementedError("M1 step 3")

    def copy_extract(self, previous: Snapshot, name: str) -> ExtractRecord:
        """Carry an unchanged extract over from an earlier snapshot (git dedupes the blob)."""
        raise NotImplementedError("M1 step 3")

    def record_fetch(self, record: FetchRecord) -> None:
        """Add a request to the manifest's ``fetched`` list."""
        raise NotImplementedError("M1 step 3")

    def set_window(self, start: date, end: date) -> None:
        raise NotImplementedError("M1 step 3")

    def set_data_date(self, day: date) -> None:
        raise NotImplementedError("M1 step 3")

    def note(self, text: str) -> None:
        raise NotImplementedError("M1 step 3")

    def close(self, *, complete: bool = True) -> Snapshot:
        """Write the manifest and rename ``<date>.tmp`` to ``<date>``."""
        raise NotImplementedError("M1 step 3")

    def abort(self) -> None:
        """Delete the temporary directory."""
        raise NotImplementedError("M1 step 3")

    def __enter__(self) -> SnapshotWriter:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, *rest: object) -> None:
        if exc_type is None:
            self.close()
        else:
            self.abort()


@dataclass(frozen=True, slots=True)
class RawDir:
    """A run's scratch directory for big raw files (clones, full dumps)."""

    path: Path
    keep: bool = False  # --keep-raw

    def file(self, name: str) -> Path:
        """Return ``path/name``, creating parent directories."""
        raise NotImplementedError("M1 step 3")

    def cleanup(self) -> None:
        """Delete the directory unless ``keep``."""
        raise NotImplementedError("M1 step 3")


@dataclass(frozen=True, slots=True)
class StoreReport:
    """Result of ``Store.check()``: failures block, warnings go in review.md."""

    failures: tuple[str, ...]
    warnings: tuple[str, ...]
    sizes: tuple[tuple[str, int], ...]  # (source, bytes) of the newest snapshots


@dataclass(frozen=True, slots=True)
class Store:
    root: Path

    @classmethod
    def from_paths(cls, paths: Paths) -> Store:
        """The store at ``paths.require_store()``."""
        raise NotImplementedError("M1 step 3")

    def sources(self) -> list[str]:
        """Source directories, sorted (names starting with ``_`` excluded)."""
        raise NotImplementedError("M1 step 3")

    def dates(self, source: str, *, complete_only: bool = True) -> list[date]:
        raise NotImplementedError("M1 step 3")

    def snapshot(self, source: str, day: date) -> Snapshot | None:
        """The complete snapshot for exactly ``day``, if any."""
        raise NotImplementedError("M1 step 3")

    def latest(
        self, source: str, on_or_before: date, *, max_age: timedelta | None = None
    ) -> Snapshot | None:
        """The newest complete snapshot not after ``on_or_before`` (and not older than ``max_age``).

        The stale policy passes ``max_age=stale_max_age(cfg.ranking.stale.max_months)``.
        """
        raise NotImplementedError("M1 step 3")

    def writer(
        self,
        source: str,
        day: date,
        collector_version: int,
        *,
        refetch: bool = False,
        frozen: frozenset[date] = frozenset(),
    ) -> SnapshotWriter:
        """Open a writer; raises ``SnapshotExists`` or ``SnapshotFrozen`` as the rules say."""
        raise NotImplementedError("M1 step 3")

    def raw_dir(self, paths: Paths, run_id: str, *, keep: bool = False) -> RawDir:
        raise NotImplementedError("M1 step 3")

    def write_run(self, day: date, run: dict[str, Any]) -> Path:
        """Write ``_runs/<day>.json``."""
        raise NotImplementedError("M1 step 3")

    def check(self, *, run_date: date | None = None) -> StoreReport:
        """Size limits per extract, snapshot and run; repository size; growth."""
        raise NotImplementedError("M1 step 3")

    def gc(self, raw_root: Path, older_than: timedelta) -> list[Path]:
        """Delete raw run directories older than ``older_than``; return what was removed."""
        raise NotImplementedError("M1 step 3")

    def commit(self, message: str) -> str | None:
        """``git add -A``, commit, ``pull --rebase`` and push (unless TFF_STORE_PUSH=0).

        Returns the new commit sha, or None when nothing changed.
        """
        raise NotImplementedError("M1 step 3")


# --- tff-catalog store {ls,check,commit,gc} ------------------------------------


def cmd_ls(paths: Paths, source: str | None = None) -> int:
    """List sources, or one source's snapshot dates with sizes and completeness."""
    raise NotImplementedError("M1 step 3")


def cmd_check(paths: Paths) -> int:
    """Run ``Store.check``; non-zero exit on any failure."""
    raise NotImplementedError("M1 step 3")


def cmd_commit(paths: Paths, message: str | None = None) -> int:
    raise NotImplementedError("M1 step 3")


def cmd_gc(paths: Paths, raw_older_than: timedelta) -> int:
    raise NotImplementedError("M1 step 3")
