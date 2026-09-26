"""Unmerged runs never advance state (design-m1 §5).

State advances only when a refresh PR is merged. So, on a synthetic store and
state S0 (``tests/helpers/synth.py``):

1. a run never writes ``state/``;
2. two runs from the same inputs give byte-identical ``build/`` trees,
   ``build/state/`` included;
3. a skipped month: the November run from the unmerged S0 equals a lone
   November run, and its counters advance once from S0, not twice;
4. merging either of two identical October runs, then running November,
   gives the same output, which differs from November on S0.

Each test runs twice: on the stub pipeline in ``synth`` (which passes today)
and on the real ``refresh`` with ``tff_catalog.state``, which is xfail until
M1 step 18. When the real one passes, strict xfail fails the suite: then drop
the mark and point ``synth.make_store``'s data at the real collectors' formats.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from tests.helpers import ROOT, synth
from tests.helpers.treehash import tree_diff, treehash

from tff_catalog import refresh, state
from tff_catalog.paths import Paths

OCT = date(2026, 10, 3)
NOV = date(2026, 11, 3)


@dataclass(frozen=True, slots=True)
class Pipeline:
    refresh: Callable[..., Any]
    apply_state: Callable[..., Path]
    load_state: Callable[[Path], state.State]


PIPELINES = [
    pytest.param(Pipeline(synth.stub_refresh, synth.apply_state, synth.read_state), id="stub"),
    pytest.param(
        Pipeline(refresh.refresh, state.apply_state, state.load_state),
        id="real",
        marks=pytest.mark.xfail(
            strict=True, raises=NotImplementedError, reason="M1 step 18: real refresh"
        ),
    ),
]


@pytest.fixture(params=PIPELINES)
def pipeline(request: pytest.FixtureRequest) -> Pipeline:
    return request.param


@dataclass
class Runner:
    pipeline: Pipeline
    tmp: Path
    store: Path

    def run(self, name: str, state_dir: Path, day: date) -> Path:
        """Replay ``day``'s snapshots with ``state_dir`` as state; return the build directory."""
        work = self.tmp / name
        paths = Paths.for_root(
            ROOT, state=state_dir, store=self.store, build=work / "build", raw_root=work / "raw"
        )
        result = self.pipeline.refresh(paths, day, from_snapshots=day)
        assert result.ok, result.failures
        assert result.build == paths.build
        return result.build

    def merge(self, name: str, state_dir: Path, build: Path) -> Path:
        """Simulate merging a run's refresh PR onto a copy of ``state_dir``."""
        return self.pipeline.apply_state(state_dir, build / "state", self.tmp / name)


@pytest.fixture
def runner(pipeline: Pipeline, tmp_path: Path, synth_store: Path) -> Runner:
    return Runner(pipeline, tmp_path / "runs", synth_store)


def assert_same_tree(a: Path, b: Path) -> None:
    assert treehash(a) == treehash(b), f"trees differ at {tree_diff(a, b)}"


def outside(pipeline: Pipeline, state_dir: Path) -> dict[str, int]:
    """Catalog ``runs_outside`` counters by family id."""
    catalog = pipeline.load_state(state_dir).membership.get("catalog", {})
    return {fid: entry["runs_outside"] for fid, entry in catalog.items()}


def test_run_never_mutates_state(runner: Runner, synth_state: Path, synth_store: Path) -> None:
    state_before, store_before = treehash(synth_state), treehash(synth_store, exclude=["_runs"])
    runner.run("a", synth_state, OCT)
    assert treehash(synth_state) == state_before, "a run wrote to state/"
    assert treehash(synth_store, exclude=["_runs"]) == store_before, "a replay changed snapshots"


def test_two_unmerged_runs_are_identical(runner: Runner, synth_state: Path) -> None:
    a = runner.run("a", synth_state, OCT)
    b = runner.run("b", synth_state, OCT)
    assert (a / "state").is_dir(), "a run must write build/state/"
    assert_same_tree(a, b)


def test_skipped_month_advances_counters_once(runner: Runner, synth_state: Path) -> None:
    runner.run("oct", synth_state, OCT)  # never merged
    n1 = runner.run("n1", synth_state, NOV)
    n2 = runner.run("n2", synth_state, NOV)
    assert_same_tree(n1, n2)
    before = outside(runner.pipeline, synth_state)
    after = outside(runner.pipeline, n1 / "state")
    steps = {fid: n - before.get(fid, 0) for fid, n in after.items()}
    assert all(step <= 1 for step in steps.values()), f"counters advanced twice: {steps}"
    assert any(step == 1 for step in steps.values()), "no counter advanced; the data is too tame"


def test_merging_either_run_gives_the_same_next_run(runner: Runner, synth_state: Path) -> None:
    a = runner.run("a", synth_state, OCT)
    b = runner.run("b", synth_state, OCT)
    merged_a = runner.merge("merged-a", synth_state, a)
    merged_b = runner.merge("merged-b", synth_state, b)
    assert_same_tree(merged_a, merged_b)
    next_a = runner.run("next-a", merged_a, NOV)
    next_b = runner.run("next-b", merged_b, NOV)
    assert_same_tree(next_a, next_b)
    unmerged = runner.run("next-s0", synth_state, NOV)
    assert treehash(next_a) != treehash(unmerged), "merging October changed nothing in November"


def test_treehash_sees_every_change(tmp_path: Path) -> None:
    tree = tmp_path / "t"
    (tree / "sub").mkdir(parents=True)
    (tree / "sub" / "a.json").write_text("{}\n")
    first = treehash(tree)
    assert treehash(tree) == first
    copy = tmp_path / "copy"
    (copy / "sub").mkdir(parents=True)
    (copy / "sub" / "a.json").write_text("{}\n")
    assert treehash(copy) == first, "the hash must not depend on the tree's location"
    (tree / "sub" / "a.json").write_text("{ }\n")
    assert treehash(tree) != first
    assert tree_diff(tree, copy) == ["sub/a.json"]
    (tree / "sub" / "a.json").write_text("{}\n")
    (tree / "empty").mkdir()
    assert tree_diff(tree, copy) == ["empty"]


def test_synthetic_inputs_are_deterministic(tmp_path: Path) -> None:
    a = synth.make_store(tmp_path / "a")
    b = synth.make_store(tmp_path / "b")
    assert_same_tree(a, b)
    assert_same_tree(synth.make_state(tmp_path / "sa", a), synth.make_state(tmp_path / "sb", b))
    other = synth.make_store(tmp_path / "c", seed=synth.SEED + 1)
    assert treehash(other) != treehash(a)
    assert synth.records() == synth.records()
    assert {type(r).__name__ for r in synth.records()} == {
        "Observation",
        "UniverseRecord",
        "LicenseFact",
        "Relation",
    }


def test_stub_marks_a_missing_snapshot_stale(synth_store: Path) -> None:
    inputs = synth.load_inputs(synth_store, NOV)
    assert inputs.stale == (synth.PACKAGES,)
    assert inputs.snapshots[synth.PACKAGES] == OCT
    assert synth.load_inputs(synth_store, OCT).stale == ()
