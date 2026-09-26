"""Owner gates: questions and rulings (design-m1 §7). Owner: agent P14.

Rulings live in ``data/reviews/<dir>/<YYYY-MM-DD>.toml``, one file per
answered batch, where ``<dir>`` is ``GATE_DIRS[gate]`` (``gate_dir``): the
2026-09-25 rulings are ``data/reviews/terms/`` (gate T), ``method/`` (M) and
``site/`` (SITE). Every stage that reads rulings finds them through
``gate_dir``, never by spelling the path.

File format (``schemas/review.schema.json``; the committed files are the
examples). Comment lines at the top say who ruled, when and where else the
ruling is recorded. Each top-level table is one question, named by its id:

- ``ruling`` (required): what the answer means, in plain words;
- ``reason`` (required): why, and whose words those are;
- ``choice``: the option picked ("a", "b", ...), for a lettered question, with
  ``recommended`` (whether that was the recommended option);
- any other keys hold the answer's values for questions that are not lettered,
  for example site wording: ``label``, ``options``, ``value``.

``tff-catalog questions --gate G`` prints the open questions of a gate as
single-select questions with at most 4 options, the recommended one marked (no
multi-select: it cannot be submitted in the owner's UI).
``tff-catalog rulings apply FILE`` checks an answers file and writes it into
``data/reviews/``.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tff_catalog.paths import Paths

# Gate id -> directory under data/reviews/. Frozen contract.
GATE_DIRS: dict[str, str] = {
    "T": "terms",  # source terms (M1 step 3)
    "M": "method",  # method clarifications
    "C": "config",  # preinstalled.toml and the step 2 config
    "L": "latin",  # Latin thresholds and the dual-script allowlist
    "LIC": "licenses",  # the license queue
    "A": "aliases",
    "U": "unmatched",
    "X": "corrections",  # new preinstalled or dependency cases
    "L3": "l3",  # license verification failures
    "K": "links",  # link overrides
    "R": "review",  # the top lists
    "CI": "ci",  # refresh pull requests and the watchdog
    "SITE": "site",  # site wording (Milestone 2)
}
GATES = tuple(GATE_DIRS)
MAX_OPTIONS = 4
SCHEMA = "review.schema.json"  # under schemas/


def gate_dir(paths: Paths, gate: str) -> Path:
    """``data/reviews/<GATE_DIRS[gate]>/``; ``KeyError`` for an unknown gate."""
    return paths.reviews / GATE_DIRS[gate]


@dataclass(frozen=True, slots=True)
class Question:
    gate: str
    id: str  # "M3", "LIC-dejavu", ...
    text: str
    options: tuple[str, ...]  # at most MAX_OPTIONS
    recommended: int | None = None  # index into options


@dataclass(frozen=True, slots=True)
class Answer:
    """One question's table in a rulings file."""

    id: str  # the table name: "M9", "spacing_filter"
    ruling: str
    reason: str
    choice: str | None = None  # "a", "b", ... for a lettered question
    recommended: bool | None = None  # whether ``choice`` was the recommended option
    values: tuple[
        tuple[str, str | bool | int | float | tuple[str, ...]], ...
    ] = ()  # other keys, sorted


@dataclass(frozen=True, slots=True)
class Ruling:
    """One rulings file: ``data/reviews/<GATE_DIRS[gate]>/<day>.toml``."""

    gate: str
    day: date
    answers: tuple[Answer, ...]  # in file order


def load_rulings(paths: Paths, gate: str | None = None) -> list[Ruling]:
    """Every ruling (of ``gate``), oldest first; a later ruling overrides an earlier one."""
    raise NotImplementedError("M1 step 2")


def questions(paths: Paths, gate: str) -> list[Question]:
    """The gate's questions that have no ruling yet."""
    raise NotImplementedError("M1 step 2")


def write_ruling(paths: Paths, ruling: Ruling) -> Path:
    """Write ``data/reviews/<GATE_DIRS[gate]>/<day>.toml``."""
    raise NotImplementedError("M1 step 2")


def cmd_questions(paths: Paths, gate: str) -> int:
    """``tff-catalog questions --gate G``."""
    raise NotImplementedError("M1 step 2")


def cmd_apply_rulings(paths: Paths, file: Path) -> int:
    """``tff-catalog rulings apply FILE``."""
    raise NotImplementedError("M1 step 2")
