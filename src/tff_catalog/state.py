"""Run state carried between monthly runs (design-m1 §5). Owner: agent I2.

``state/`` on main is read-only input. A run writes the state it proposes to
``build/state/``; the refresh pull request copies that to ``state/``, so state
advances only when that PR is merged, and two unmerged runs from the same
inputs give identical output.

Every stage is its own command, so each state file has owning stages
(``STATE_OWNERS``) that write it with ``write_part``:

- the first owner starts from the committed file (``ctx.state``);
- a later owner in the same run starts from the earlier owner's file
  (``read_part``), for example ``membership`` adds catalog dates to the
  ``first_seen`` that ``correct`` wrote;
- every part is a pure function of its inputs, so a rerun writes the same bytes.

``refresh`` starts with an empty ``build/state/`` and ends with
``complete_next_state``, which copies every file no stage wrote this run from
``state/``, so ``build/state/`` always holds the whole state.

Files (all JSON, written with ``jsonio.dump``)::

    run_history.json    [{run_date, merged_pr, code_commit, config_sha256, snapshots: {source: date}}]  <= 24
    ids.json            {family_id: {family, minted_from, first_seen}}      append-only id registry
    first_seen.json     {family_id: {catalog: date|null, sources: {source: date}}}
    membership.json     {catalog: {id: {member, entered, runs_outside}}, top100: {rank_key: {id: {...}}}}
    license_hashes.json {id: {text_url, text_sha256, checked_on, font_version, font_file: {url, sha256}, level}}
    stale.json          {source: {last_good: date, stale_runs: int}}
    published_ranks.json {rank_key: {id: order}}
    smoothing.json      {fot_ewma: {id: z}, rising: {source: {id: [share_m-2, share_m-1, share_m]}}}

A missing file reads as empty, so the first run starts from nothing. Snapshot
baselines (GitHub and Nerd differences) are pointers:
``run_history[*].snapshots``. Owner rulings stay in ``data/reviews/``.
"""

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tff_catalog import jsonio

if TYPE_CHECKING:
    from tff_catalog.paths import Paths

STATE_FILES: dict[str, str] = {
    "run_history": "run_history.json",
    "ids": "ids.json",
    "first_seen": "first_seen.json",
    "membership": "membership.json",
    "license_hashes": "license_hashes.json",
    "stale": "stale.json",
    "published_ranks": "published_ranks.json",
    "smoothing": "smoothing.json",
}
MAX_RUN_HISTORY = 24

# The stages that write each state file, in pipeline order. Frozen contract.
STATE_OWNERS: dict[str, tuple[str, ...]] = {
    "stale": ("parse",),
    "ids": ("universe",),
    "first_seen": ("correct", "membership"),  # sources' first days, then catalog entry dates
    "smoothing": ("rank",),
    "membership": ("membership",),
    "license_hashes": ("verify",),
    "published_ranks": ("export",),
    "run_history": ("refresh",),
}
_EMPTY: dict[str, Any] = {"run_history": []}


def read_part(paths: Paths, name: str) -> Any:
    """State file ``name`` as this run has it so far: ``build/state/`` if a stage wrote
    it, else the committed ``state/`` file, else empty."""
    filename = STATE_FILES[name]
    for directory in (paths.next_state, paths.state):
        if (directory / filename).is_file():
            return jsonio.load(directory / filename)
    return _EMPTY.get(name, {})


def write_part(paths: Paths, name: str, obj: object, *, stage: str) -> Path:
    """Write state file ``name`` into ``build/state/``; only its ``STATE_OWNERS`` may."""
    if name not in STATE_FILES:
        raise KeyError(f"unknown state file {name!r}; known: {', '.join(STATE_FILES)}")
    if stage not in STATE_OWNERS[name]:
        raise PermissionError(f"stage {stage!r} may not write state {name!r}")
    path = paths.next_state / STATE_FILES[name]
    jsonio.dump(obj, path)
    return path


def complete_next_state(paths: Paths) -> list[str]:
    """Copy each state file no stage wrote this run from ``state/`` into ``build/state/``.

    Returns the names copied. A file missing from both stays missing (it reads as empty).
    """
    copied = []
    for name, filename in STATE_FILES.items():
        source, target = paths.state / filename, paths.next_state / filename
        if not target.exists() and source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            copied.append(name)
    return copied


@dataclass(frozen=True, slots=True)
class State:
    """The committed state a run starts from. Never mutated."""

    run_history: tuple[dict[str, Any], ...] = ()
    ids: dict[str, dict[str, Any]] = field(default_factory=dict)
    first_seen: dict[str, dict[str, Any]] = field(default_factory=dict)
    membership: dict[str, Any] = field(default_factory=dict)
    license_hashes: dict[str, dict[str, Any]] = field(default_factory=dict)
    stale: dict[str, dict[str, Any]] = field(default_factory=dict)
    published_ranks: dict[str, dict[str, int]] = field(default_factory=dict)
    smoothing: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NextState:
    """The whole proposed state in memory, for ``refresh`` and tests.

    Stages do not pass one around (each is its own command): they write their
    parts with ``write_part``. ``write_next_state`` writes a whole one at once.
    """

    base: State
    run_history: list[dict[str, Any]] = field(default_factory=list)
    ids: dict[str, dict[str, Any]] = field(default_factory=dict)
    first_seen: dict[str, dict[str, Any]] = field(default_factory=dict)
    membership: dict[str, Any] = field(default_factory=dict)
    license_hashes: dict[str, dict[str, Any]] = field(default_factory=dict)
    stale: dict[str, dict[str, Any]] = field(default_factory=dict)
    published_ranks: dict[str, dict[str, int]] = field(default_factory=dict)
    smoothing: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_state(cls, state: State) -> NextState:
        """Start from a deep copy of ``state``."""
        raise NotImplementedError("M1 step 3")


def load_state(path: Path) -> State:
    """Read ``state/`` (or any directory of the same files); missing files read as empty."""
    raise NotImplementedError("M1 step 3")


def write_next_state(next_state: NextState, path: Path) -> None:
    """Write every state file to ``path`` (normally ``build/state/``), deterministically."""
    raise NotImplementedError("M1 step 3")


def apply_state(state_dir: Path, next_state_dir: Path, out_dir: Path | None = None) -> Path:
    """Simulate merging a refresh PR: ``next_state_dir``'s files over ``state_dir``'s.

    Writes into ``out_dir`` (a copy) or, when it is None, into ``state_dir``
    itself; returns the directory written.
    """
    raise NotImplementedError("M1 step 3")
