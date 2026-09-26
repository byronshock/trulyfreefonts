"""Collector discovery (design-m1 §2.3). Frozen contract.

Collectors live in ``collectors/universe/`` and ``collectors/ranking/``, one
module per collector, each exposing ``COLLECTOR``. Modules whose names start
with ``_`` are skipped. The module name, the collector's ``name`` and its store
directory are the same string.
"""

import importlib
import pkgutil

from tff_catalog.collectors import ranking, universe
from tff_catalog.collectors.base import Collector


def discover(kind: str | None = None) -> dict[str, Collector]:
    """Every collector (of ``kind``, when given), sorted by name."""
    out: dict[str, Collector] = {}
    for pkg in (universe, ranking):
        for m in pkgutil.iter_modules(pkg.__path__):
            if m.name.startswith("_"):
                continue
            module = importlib.import_module(f"{pkg.__name__}.{m.name}")
            c = getattr(module, "COLLECTOR", None)
            if not isinstance(c, Collector) or c.name != m.name:
                raise TypeError(f"{module.__name__}.COLLECTOR must be a Collector named {m.name!r}")
            if c.name in out:
                raise TypeError(f"collector {c.name!r} is defined twice")
            if kind is None or c.kind == kind:
                out[c.name] = c
    return dict(sorted(out.items()))


def get(name: str) -> Collector:
    """The collector called ``name``; ``KeyError`` lists the known names."""
    found = discover()
    try:
        return found[name]
    except KeyError:
        raise KeyError(f"unknown collector {name!r}; known: {', '.join(found) or 'none'}") from None
