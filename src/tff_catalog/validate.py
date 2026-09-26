"""Stage "validate": schemas and the hard checks (methodology §9, milestone-1 step 15). Owner: agent P12.

Hard failures block the refresh pull request: an ineligible font ranked; a
flagged license missing from the queue; a schema failure; a rerun from the
same snapshots giving different output; an ineligible font moving any rank; a
failed known answer (Source Sans Pro → Source Sans 3, Sauce Code Pro → Source
Code Pro, Roboto Slab gets no Roboto counts, a renamed family keeps its id); a
higher count lowering a rank without the guard; the desktop views differing
except by abstentions; an abstaining Linux count moving the overall rank; a
raw source ``value`` in ``catalog.json`` (or any public output) for a source
whose ``publish_raw`` is false (rulings T2 and T4: Google and Fonts Over Time
publish ranks and rank-based z only).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tff_catalog.stages import StageContext


class ValidationFailed(RuntimeError):
    """At least one hard check failed; the message lists them."""


@dataclass(frozen=True, slots=True)
class Failure:
    check: str
    message: str
    family_id: str | None = None


def schema_errors(path: Path, schema: Path) -> list[str]:
    """Every JSON Schema (2020-12) error of the document at ``path``, as "pointer: message"."""
    raise NotImplementedError("M1 step 15")


def hard_checks(ctx: StageContext) -> list[Failure]:
    """Run every §9 hard check on the build outputs."""
    raise NotImplementedError("M1 step 15")


def run(ctx: StageContext) -> None:
    """Stage "validate": raise ``ValidationFailed`` if anything failed."""
    raise NotImplementedError("M1 step 15")
