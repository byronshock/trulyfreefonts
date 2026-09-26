"""Alias miners (design-m1 §2.3), discovered like collectors. Frozen contract.

Each miner is a module ``aliases/miners/<name>.py`` exposing ``MINER``, an
object satisfying ``Miner``. It proposes aliases from one kind of evidence and
writes them to ``data/alias-seeds/<name>.csv`` with ``aliases.write_seeds``.
A miner never writes ``data/aliases.csv``.
"""

import importlib
import logging
import pkgutil
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import ClassVar, Protocol, runtime_checkable

from tff_catalog.aliases import AliasCandidate
from tff_catalog.paths import Paths
from tff_catalog.store import RawDir, Store


@dataclass(frozen=True, slots=True)
class MineContext:
    paths: Paths
    store: Store | None  # snapshots of the collectors, read-only
    raw: RawDir  # scratch space for clones (gf_history's blobless clone)
    run_date: date
    log: logging.Logger


@runtime_checkable
class Miner(Protocol):
    name: ClassVar[str]  # == module name == seed file name

    def mine(self, ctx: MineContext) -> Iterable[AliasCandidate]:
        """Propose aliases. Deterministic for the same inputs."""
        ...


def discover() -> dict[str, Miner]:
    """Every miner, sorted by name. Modules starting with ``_`` are skipped."""
    pkg = sys.modules[__name__]
    out: dict[str, Miner] = {}
    for m in pkgutil.iter_modules(pkg.__path__):
        if m.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{m.name}")
        miner = getattr(module, "MINER", None)
        if not isinstance(miner, Miner) or miner.name != m.name:
            raise TypeError(f"{module.__name__}.MINER must be a Miner named {m.name!r}")
        out[miner.name] = miner
    return dict(sorted(out.items()))


def get(name: str) -> Miner:
    """The miner called ``name``; ``KeyError`` lists the known names."""
    found = discover()
    try:
        return found[name]
    except KeyError:
        raise KeyError(f"unknown miner {name!r}; known: {', '.join(found) or 'none'}") from None
