"""The only module allowed to read the wall clock.

Everything else asks this module for the time, so a test can freeze it in one
place. Call it as ``clock.utc_now()`` (not ``from tff_catalog.clock import
utc_now``) or use ``frozen()``, which works whichever way it was imported.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime

_frozen: datetime | None = None


def utc_now() -> datetime:
    """Return the current time as an aware UTC datetime, or the frozen time."""
    if _frozen is not None:
        return _frozen
    return datetime.now(UTC)


def utc_today() -> date:
    """Return today's UTC date, the default ``--date`` of every command."""
    return utc_now().date()


def iso_utc(moment: datetime) -> str:
    """Format an aware datetime as ``2026-10-03T06:17:22Z`` (whole seconds, UTC)."""
    if moment.tzinfo is None:
        raise ValueError("iso_utc needs an aware datetime")
    return moment.astimezone(UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


@contextmanager
def frozen(moment: datetime) -> Iterator[datetime]:
    """Freeze ``utc_now()`` at ``moment`` (aware) inside the ``with`` block."""
    global _frozen
    if moment.tzinfo is None:
        raise ValueError("frozen needs an aware datetime")
    previous, _frozen = _frozen, moment.astimezone(UTC)
    try:
        yield _frozen
    finally:
        _frozen = previous
