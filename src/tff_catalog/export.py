"""Stages "export" and "export-site" (milestone-1 step 15). Owner: agent P12.

- "export" (15) writes ``build/catalog.json`` (``schemas/catalog.schema.json``,
  methodology §7) from every stage output.
- "specimens" (15b, Milestone 2) runs between them and fills ``preview``.
- "export-site" (15c) writes ``build/catalog-site.json``
  (``schemas/catalog-site.schema.json``) and ``build/names.json``
  (``schemas/names.schema.json``): the names and aliases of every eligible
  family in the universe, not only the catalog.

Raw source values appear only where ``ranking.toml`` ``publish_raw`` allows.
Output is canonical (``jsonio.dump``), so the same inputs give the same bytes.

Every piece of site wording comes from ``config/site.toml`` (``cfg.site``),
never from code or the sample: ``data_license``, ``views`` (``available`` is
computed: Rising needs ``ranks.rising.min_history_months`` of history),
``tiers``, ``license_classes``, the source credits (``sources[].name``,
``measures``, ``url``, ``license``, ``publish_rank``; ``group`` and ``survey``
come from ``ranking.toml``) and the labels of package systems. Preinstalled
systems take their labels from ``preinstalled.toml``. Band labels are derived
from ``ranking.toml [display]``: "<from>\u2013<to>" (an en dash), and
"<from>+" for the open band.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tff_catalog.stages import StageContext

CATALOG_SCHEMA_VERSION = "0.1.0-draft"
NAMES_SCHEMA_VERSION = "0.1.0-draft"
SITE_SCHEMA_VERSION = "1.0.0-draft"  # catalog-site.schema.json's const


def build_catalog(ctx: StageContext) -> dict[str, Any]:
    """The ``catalog.json`` document."""
    raise NotImplementedError("M1 step 15")


def build_site(catalog: dict[str, Any], ctx: StageContext) -> dict[str, Any]:
    """The trimmed ``catalog-site.json`` document for the filterable list."""
    raise NotImplementedError("M1 step 15")


def build_names(ctx: StageContext) -> dict[str, Any]:
    """The ``names.json`` document for owned-font matching (Milestone 3)."""
    raise NotImplementedError("M1 step 15")


def run(ctx: StageContext) -> None:
    """Stage "export": write ``build/catalog.json``."""
    raise NotImplementedError("M1 step 15")


def run_site(ctx: StageContext) -> None:
    """Stage "export-site": write ``build/catalog-site.json`` and ``build/names.json``."""
    raise NotImplementedError("M1 step 15")
