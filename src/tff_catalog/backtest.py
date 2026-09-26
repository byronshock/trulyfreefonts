"""Backtest of month-to-month churn on historical windows (milestone-1 step 13). Owner: agent P10.

Windows: the pkgstats monthly series, 18 months of npm, Homebrew 30/90/365
days and Google's windows. The report sets the alert thresholds in
``ranking.toml [review]`` and is committed as ``docs/backtests/<date>.md``.
Runs on its own (``tff-catalog backtest``), never inside refresh.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tff_catalog.stages import StageContext


@dataclass(frozen=True, slots=True)
class BacktestReport:
    windows: tuple[str, ...]
    rbo: tuple[tuple[str, float], ...]  # (window pair, rank-biased overlap)
    spearman: tuple[tuple[str, float], ...]
    suggested: tuple[tuple[str, float], ...]  # (ranking.toml [review] key, value)


def backtest(ctx: StageContext) -> BacktestReport:
    """Compute churn between consecutive historical windows."""
    raise NotImplementedError("M1 step 13")


def render(report: BacktestReport) -> str:
    """The Markdown report."""
    raise NotImplementedError("M1 step 13")


def run(ctx: StageContext) -> None:
    """``tff-catalog backtest``: write ``docs/backtests/<run_date>.md``."""
    raise NotImplementedError("M1 step 13")
