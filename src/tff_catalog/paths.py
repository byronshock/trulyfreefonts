"""Where everything lives: the repository, the snapshot store and raw downloads.

Standard library only, because ``tff_site`` imports it.

- The repository root is the nearest directory, from the current one upwards,
  whose ``pyproject.toml`` names the ``tff-catalog`` project. That keeps every
  git worktree self-contained.
- ``TFF_STORE`` points at the clone of the private data repository. It has no
  default inside the repo; commands that need it call ``require_store()``,
  which fails with a clear message when it is unset.
- ``TFF_RAW`` is the parent of per-run raw directories (default
  ``~/.cache/tff/raw``); a run's big raw files go in ``raw_dir(run_id)``.
"""

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

PROJECT_NAME = "tff-catalog"
STORE_ENV = "TFF_STORE"
RAW_ENV = "TFF_RAW"
DEFAULT_RAW = Path("~/.cache/tff/raw")


class StoreNotConfigured(RuntimeError):
    """``TFF_STORE`` is unset, or does not point at a directory."""


def find_root(start: Path | None = None) -> Path:
    """Return the repository root at or above ``start`` (default: the current directory)."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        pyproject = candidate / "pyproject.toml"
        if pyproject.is_file() and _is_project(pyproject):
            return candidate
    raise FileNotFoundError(
        f"no {PROJECT_NAME} checkout at or above {here}; run inside the repository"
    )


def _is_project(pyproject: Path) -> bool:
    try:
        with pyproject.open("rb") as fh:
            return tomllib.load(fh).get("project", {}).get("name") == PROJECT_NAME
    except OSError, tomllib.TOMLDecodeError:
        return False


@dataclass(frozen=True, slots=True)
class Paths:
    """Resolved locations for one run. Tests build one with ``for_root``."""

    root: Path
    config: Path
    data: Path
    state: Path  # read-only input: the committed run state on main
    build: Path
    schemas: Path
    store: Path | None  # None when TFF_STORE is unset
    raw_root: Path

    @classmethod
    def from_env(cls, root: Path | None = None, env: Mapping[str, str] | None = None) -> Paths:
        """Resolve paths from ``root`` (default: ``find_root()``) and the environment."""
        env = os.environ if env is None else env
        base = (root or find_root()).resolve()
        store = env.get(STORE_ENV) or None
        raw = env.get(RAW_ENV) or str(DEFAULT_RAW)
        return cls.for_root(
            base,
            store=Path(store).expanduser().resolve() if store else None,
            raw_root=Path(raw).expanduser(),
        )

    @classmethod
    def for_root(
        cls,
        root: Path,
        *,
        state: Path | None = None,
        store: Path | None = None,
        raw_root: Path | None = None,
        build: Path | None = None,
    ) -> Paths:
        """Lay out the standard tree under ``root``, overriding any part given."""
        return cls(
            root=root,
            config=root / "config",
            data=root / "data",
            state=state or root / "state",
            build=build or root / "build",
            schemas=root / "schemas",
            store=store,
            raw_root=raw_root or DEFAULT_RAW.expanduser(),
        )

    def with_(self, **changes: Path | None) -> Paths:
        """Return a copy with some fields replaced."""
        return replace(self, **changes)

    # config/
    @property
    def sources_config(self) -> Path:
        """``config/sources/``: one strict settings file per collector."""
        return self.config / "sources"

    # data/
    @property
    def aliases_csv(self) -> Path:
        return self.data / "aliases.csv"

    @property
    def alias_seeds(self) -> Path:
        return self.data / "alias-seeds"

    @property
    def superfamilies_csv(self) -> Path:
        return self.data / "superfamilies.csv"

    @property
    def reviews(self) -> Path:
        """``data/reviews/``: the owner's rulings, one directory per gate (``reviews.gate_dir``)."""
        return self.data / "reviews"

    # build/
    @property
    def stage(self) -> Path:
        """``build/stage/``: intermediates, gitignored."""
        return self.build / "stage"

    @property
    def records(self) -> Path:
        return self.stage / "records"

    @property
    def queues(self) -> Path:
        return self.stage / "queues"

    @property
    def next_state(self) -> Path:
        """``build/state/``: the state this run proposes; the refresh PR copies it to ``state/``."""
        return self.build / "state"

    @property
    def cache(self) -> Path:
        return self.build / "cache"

    @property
    def specimens(self) -> Path:
        """``build/specimens/``: committed SVG specimens (M2)."""
        return self.build / "specimens"

    def require_store(self) -> Path:
        """Return the snapshot store, or raise ``StoreNotConfigured`` with a fix-it message."""
        if self.store is None:
            raise StoreNotConfigured(
                f"{STORE_ENV} is not set. Point it at your clone of the private data "
                f"repository, for example: export {STORE_ENV}=~/Documents/code/trulyfreefonts-data"
            )
        if not self.store.is_dir():
            raise StoreNotConfigured(f"{STORE_ENV}={self.store} is not a directory")
        return self.store

    def raw_dir(self, run_id: str) -> Path:
        """Directory for one run's big raw downloads (deleted after the run unless kept)."""
        return self.raw_root.expanduser() / run_id
