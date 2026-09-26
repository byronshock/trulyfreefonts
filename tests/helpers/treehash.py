"""A stable hash of a directory tree.

``treehash(path)`` depends only on the relative paths (POSIX form), the kind of
each entry and file contents: never on timestamps, permissions, the absolute
location or the order the file system lists entries in. Two runs that write
the same files give the same hash; ``tree_diff`` says which paths differ.
"""

import hashlib
from collections.abc import Iterable
from pathlib import Path


def tree_entries(root: Path, exclude: Iterable[str] = ()) -> dict[str, str]:
    """Map each relative path under ``root`` to ``"dir"``, ``"link:<target>"`` or the file's sha256.

    Any path with a component named in ``exclude`` (``"__pycache__"``, say) is left out.
    """
    root = Path(root)
    if not root.exists():
        raise FileNotFoundError(root)
    skip = frozenset(exclude)
    if root.is_file():
        return {root.name: _file_sha256(root)}
    out: dict[str, str] = {}
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if skip.intersection(rel.parts):
            continue
        key = rel.as_posix()
        if path.is_symlink():
            out[key] = f"link:{path.readlink().as_posix()}"
        elif path.is_dir():
            out[key] = "dir"
        else:
            out[key] = _file_sha256(path)
    return dict(sorted(out.items()))


def treehash(root: Path, exclude: Iterable[str] = ()) -> str:
    """Return the sha256 (hex) of the tree under ``root``."""
    h = hashlib.sha256()
    for key, value in tree_entries(root, exclude).items():
        h.update(key.encode("utf-8"))
        h.update(b"\0")
        h.update(value.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def tree_diff(a: Path, b: Path, exclude: Iterable[str] = ()) -> list[str]:
    """Relative paths that differ between two trees (added, removed or changed), sorted."""
    left = tree_entries(a, exclude)
    right = tree_entries(b, exclude)
    return sorted(k for k in left.keys() | right.keys() if left.get(k) != right.get(k))


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()
