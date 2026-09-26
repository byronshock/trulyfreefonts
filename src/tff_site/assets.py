"""Concatenate the JS and CSS parts into one script and one stylesheet, and hash asset names.

The parts rule (site/CONTRACT.md, "JS parts"): the build concatenates ``site/js/*.js`` in
filename order into one ES module, ``/assets/app.<h>.js``, and ``site/css/*.css`` the same
way into ``/assets/style.<h>.css``. Each JS part declares exactly one top-level ``const``,
named in ``JS_PARTS``. The lint refuses extra top-level declarations, ``import``/``export``,
HTML-string APIs, ``eval``, ``Function(``, ``document.write`` and absolute URLs in ``fetch``.

Every file under ``/assets/`` is named ``<stem>.<h>.<ext>``, where ``<h>`` is the first
``HASH_LEN`` hex digits of the sha256 of its bytes, so it can be cached as immutable.
"""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

HASH_LEN = 10

# (file, top-level const) in concatenation order; must match site/CONTRACT.md.
JS_PARTS: tuple[tuple[str, str], ...] = (
    ("00-core.js", "Core"),
    ("05-keys.js", "Keys"),
    ("10-data.js", "Data"),
    ("15-state.js", "State"),
    ("20-view.js", "View"),
    ("25-render.js", "Render"),
    ("30-filters-ui.js", "FiltersUI"),
    ("35-announce.js", "Announce"),
    ("40-details.js", "Details"),
    ("45-specimens.js", "Specimens"),
    ("50-ext.js", "Ext"),
    ("90-main.js", "Main"),
)
CSS_PARTS: tuple[str, ...] = (
    "00-tokens.css",
    "10-base.css",
    "20-list.css",
    "25-filters.css",
    "30-details.css",
    "35-specimens.css",
    "40-pages.css",
)
# Substrings the JS lint refuses anywhere in a part (comments included, to keep the lint dumb).
FORBIDDEN_JS: tuple[str, ...] = (
    "innerHTML",
    "outerHTML",
    "insertAdjacentHTML",
    "eval(",
    "Function(",
    "document.write",
)


@dataclass(frozen=True, slots=True)
class AssetManifest:
    """Logical name to hashed URL, for example ``{"app.js": "/assets/app.1a2b3c4d5e.js"}``."""

    urls: dict[str, str] = field(default_factory=dict)


def content_hash(data: bytes) -> str:
    """Return the asset hash of ``data``: the first ``HASH_LEN`` hex digits of its sha256."""
    return hashlib.sha256(data).hexdigest()[:HASH_LEN]


def hashed_name(name: str, data: bytes) -> str:
    """Return ``name`` with its content hash before the extension: ``app.js`` -> ``app.<h>.js``."""
    stem, dot, ext = name.rpartition(".")
    if not dot:
        return f"{name}.{content_hash(data)}"
    return f"{stem}.{content_hash(data)}.{ext}"


def lint_js_part(filename: str, source: str) -> list[str]:
    """Return parts-rule violations in one JS part; an empty list means it passes."""
    raise NotImplementedError("M2 step 1")


def concat_js(parts_dir: Path) -> str:
    """Lint and concatenate ``parts_dir/*.js`` in filename order into one ES module."""
    raise NotImplementedError("M2 step 1")


def concat_css(parts_dir: Path) -> str:
    """Concatenate ``parts_dir/*.css`` in filename order into one stylesheet."""
    raise NotImplementedError("M2 step 1")


def write_hashed(out_dir: Path, name: str, data: bytes) -> str:
    """Write ``data`` as ``out_dir/assets/<hashed name>`` and return its URL path."""
    raise NotImplementedError("M2 step 1")
