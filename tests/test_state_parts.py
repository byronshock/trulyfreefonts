"""How stages contribute their parts of ``build/state/`` (``state.STATE_OWNERS``)."""

from pathlib import Path

import pytest

from tff_catalog import jsonio, stages, state
from tff_catalog.paths import Paths


def test_every_state_file_has_owning_stages() -> None:
    assert set(state.STATE_OWNERS) == set(state.STATE_FILES)
    known = {*stages.names(), "refresh"}
    order = [*stages.names(), "refresh"]
    for name, owners in state.STATE_OWNERS.items():
        assert owners, name
        assert set(owners) <= known, name
        assert list(owners) == sorted(owners, key=order.index), f"{name}: owners out of order"


def test_write_part_checks_the_owner(tmp_path: Path) -> None:
    paths = Paths.for_root(tmp_path)
    path = state.write_part(paths, "ids", {"inter": {"family": "Inter"}}, stage="universe")
    assert path == paths.next_state / "ids.json"
    assert jsonio.load(path) == {"inter": {"family": "Inter"}}
    with pytest.raises(PermissionError, match="may not write"):
        state.write_part(paths, "ids", {}, stage="rank")
    with pytest.raises(KeyError, match="unknown state file"):
        state.write_part(paths, "bogus", {}, stage="rank")


def test_read_part_prefers_this_runs_file(tmp_path: Path) -> None:
    paths = Paths.for_root(tmp_path)
    assert state.read_part(paths, "first_seen") == {}
    assert state.read_part(paths, "run_history") == []
    jsonio.dump({"a": {"catalog": None}}, paths.state / "first_seen.json")
    assert state.read_part(paths, "first_seen") == {"a": {"catalog": None}}
    state.write_part(paths, "first_seen", {"a": {"catalog": "2026-10-03"}}, stage="correct")
    assert state.read_part(paths, "first_seen") == {"a": {"catalog": "2026-10-03"}}


def test_complete_next_state_copies_only_unwritten_files(tmp_path: Path) -> None:
    paths = Paths.for_root(tmp_path)
    jsonio.dump({"old": 1}, paths.state / "ids.json")
    jsonio.dump({"old": 2}, paths.state / "stale.json")
    state.write_part(paths, "stale", {"new": 3}, stage="parse")
    assert state.complete_next_state(paths) == ["ids"]
    assert jsonio.load(paths.next_state / "ids.json") == {"old": 1}
    assert jsonio.load(paths.next_state / "stale.json") == {"new": 3}
    assert not (paths.next_state / "smoothing.json").exists()
    assert jsonio.load(paths.state / "stale.json") == {"old": 2}  # state/ is never written
