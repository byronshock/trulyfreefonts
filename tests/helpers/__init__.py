"""Shared test helpers (design-m1 §2.3 and §5).

- ``treehash``: a stable sha256 of a directory tree, for "same output twice" checks.
- ``mockhttp``: replays recorded HTTP responses through ``httpx.MockTransport``,
  and serves git fixtures from local repositories.
- ``synth``: synthetic records, a synthetic snapshot store and state, and a stub
  pipeline, all deterministic by seed.
- ``regen``: loads a collector's fixture snapshot, parses it, and rewrites its
  golden ``expected.jsonl`` (``uv run python -m tests.helpers.regen <collector>``).
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # the repository (or worktree) root
FIXTURES = ROOT / "tests" / "fixtures"
