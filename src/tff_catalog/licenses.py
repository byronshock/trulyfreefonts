"""Stage "licenses": L1 and L2 classification before ranking (milestone-1 step 6a). Owner: agent P3.

- L1 ``normalize``: every license string to an SPDX expression through
  ``config/license-aliases.toml``; unknown strings give None (and a queue entry).
- ``classify``: the SPDX expression to a class through ``config/licenses.toml``
  (D3); anything not listed is excluded.
- L2 ``cross_check``: the google/fonts folder, Fontsource, Fontist, Nerd Fonts,
  Debian DEP-5 and Arch must agree; disagreements go to the queue.

Writes ``build/stage/licenses.json`` ({id: Verdict}) and
``build/stage/queues/licenses.json``. Owner rulings come from gate LIC
(``reviews.gate_dir(paths, "LIC")``, that is ``data/reviews/licenses/``).
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from tff_catalog.config_model import LicensesConfig
    from tff_catalog.records import LicenseFact
    from tff_catalog.stages import StageContext


@dataclass(frozen=True, slots=True)
class LicenseClass:
    spdx: str
    status: Literal["allowed", "excluded", "ruling"]
    group: str | None = None  # license-class filter group, for allowed licenses
    redistributable: bool | None = None
    attribution_required: bool | None = None
    reason: str | None = None  # for excluded and ruling


@dataclass(frozen=True, slots=True)
class Verdict:
    family_id: str
    spdx: str | None  # the agreed expression
    license: LicenseClass | None
    preview_ok: bool  # D3: redistributable fonts only
    seen: tuple[tuple[str, str | None], ...]  # (source, normalised spdx), sorted
    queue: str | None = None  # why it needs the owner, if it does


def normalize(raw: str, source: str, table: Mapping[str, str]) -> str | None:
    """L1: ``raw`` as ``source`` wrote it, to an SPDX expression, or None if unknown."""
    raise NotImplementedError("M1 step 6a")


def classify(expr: str, cfg: LicensesConfig) -> LicenseClass:
    """The class of an SPDX expression (``OR``: the best allowed branch; ``AND``: all must pass)."""
    raise NotImplementedError("M1 step 6a")


def cross_check(
    family_id: str, facts: Sequence[LicenseFact], table: Mapping[str, str], cfg: LicensesConfig
) -> Verdict:
    """L2: combine every source's license fact for one family."""
    raise NotImplementedError("M1 step 6a")


def run(ctx: StageContext) -> None:
    """Stage "licenses"."""
    raise NotImplementedError("M1 step 6a")


def cmd_queue(ctx: StageContext, *, count: bool = False) -> int:
    """``licenses --queue [--count]``: print the review queue (or its size)."""
    raise NotImplementedError("M1 step 6a")
