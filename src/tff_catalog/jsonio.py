"""Deterministic JSON reading and writing.

Standard library only, because ``tff_site`` imports it.

- ``canonical_bytes``: compact, sorted keys, UTF-8, no NaN or infinity. Two
  equal objects always give identical bytes; hashes and "same output twice"
  checks use it.
- ``dump`` writes the pretty form (2-space indent, sorted keys, trailing
  newline) for files people read or diff; ``dump_jsonl`` writes one canonical
  object per line.
- A path ending in ``.gz`` is gzipped with a zero timestamp, so the bytes stay
  stable across runs.
- Dates become ISO strings and aware datetimes become ``...Z`` UTC strings.
  Sets, naive datetimes and other objects are refused: callers convert them
  first, so nothing depends on iteration order or local time.
- Every write is atomic: a temporary file in the same directory, then rename.
"""

import gzip
import json
import os
import tempfile
from collections.abc import Iterable, Iterator
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any


def _default(obj: object) -> object:
    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            raise TypeError(f"naive datetime {obj!r} is not JSON-safe; use clock.utc_now()")
        return obj.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"{type(obj).__name__} is not JSON-serialisable here: {obj!r}")


def canonical_str(obj: object) -> str:
    """Return the canonical JSON text of ``obj`` (compact, sorted keys, no NaN)."""
    return json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
        default=_default,
    )


def canonical_bytes(obj: object) -> bytes:
    """Return the canonical JSON bytes of ``obj``; equal objects give equal bytes."""
    return canonical_str(obj).encode("utf-8")


def pretty_bytes(obj: object) -> bytes:
    """Return the pretty, still deterministic, form used by ``dump``."""
    text = json.dumps(
        obj, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False, default=_default
    )
    return (text + "\n").encode("utf-8")


def _encode_for(path: Path, data: bytes) -> bytes:
    if path.suffix == ".gz":
        return gzip.compress(data, compresslevel=9, mtime=0)
    return data


def _read(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix == ".gz":
        return gzip.decompress(data)
    return data


def atomic_write(path: Path, data: bytes) -> None:
    """Write ``data`` to ``path`` atomically, creating parent directories."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        Path(tmp).replace(path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def dump(obj: object, path: Path) -> None:
    """Write ``obj`` as pretty JSON (gzipped when ``path`` ends in ``.gz``)."""
    path = Path(path)
    atomic_write(path, _encode_for(path, pretty_bytes(obj)))


def load(path: Path) -> Any:
    """Read one JSON document (gunzipped when ``path`` ends in ``.gz``)."""
    path = Path(path)
    return json.loads(_read(path))


def dump_jsonl(rows: Iterable[object], path: Path) -> int:
    """Write one canonical JSON object per line; return the number of rows.

    Rows are written in the order given: sort them first when the order must be
    stable (``records.sort_key`` for records).
    """
    path = Path(path)
    lines = [canonical_bytes(row) + b"\n" for row in rows]
    atomic_write(path, _encode_for(path, b"".join(lines)))
    return len(lines)


def iter_jsonl(path: Path) -> Iterator[Any]:
    """Yield the objects of a JSON Lines file, skipping blank lines."""
    path = Path(path)
    for number, line in enumerate(_read(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: {exc.msg}") from exc


def load_jsonl(path: Path) -> list[Any]:
    """Read a whole JSON Lines file into a list."""
    return list(iter_jsonl(path))
