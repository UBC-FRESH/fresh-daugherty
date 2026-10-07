"""Invariants over the tracked experiment records (P14.2 #77; extended in P16.6 #97).

These tests read the committed CSVs under ``results/experiments/`` (no solves),
so stale or corrupted records fail CI even when the code that produced them
has since changed. The E3 defect fixed in P14 (#75) would have been caught
here: the realized period-1 harvest *is* the open-loop period-1 decision, so
period-1 announced must equal period-1 realized in every cell of every grid.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RECORDS = Path(__file__).resolve().parents[1] / "results" / "experiments"


@pytest.mark.parametrize(
    "name",
    [
        "grid_trajectories.csv",
        "grid_discount_paths_trajectories.csv",
        "grid_rolling_mean_trajectories.csv",
        "grid_cap_search_trajectories.csv",
        "grid_value_flow_trajectories.csv",
    ],
)
def test_period1_announced_equals_realized(name: str) -> None:
    df = pd.read_csv(RECORDS / name)
    first = df[df["period"] == 1]
    assert len(first) > 0
    bad = first[~np.isclose(first["projected_mcf"], first["realized_mcf"], rtol=1e-6, atol=1e-6)]
    assert bad.empty, f"{len(bad)}/{len(first)} cells violate the period-1 invariant:\n{bad.head()}"


@pytest.mark.parametrize(
    "name",
    [
        "grid_institutions_trajectories.csv",
        "grid_seeds_trajectories.csv",
    ],
)
def test_period1_invariant_new_grids(name: str) -> None:
    """P16.6 (#97): the period-1 invariant on the P15 grids too."""
    test_period1_announced_equals_realized(name)


SUMMARIES = [
    "grid.csv",
    "grid_discount_paths.csv",
    "grid_cap_search.csv",
    "grid_value_flow.csv",
    "grid_rolling_mean.csv",
    "grid_institutions.csv",
    "grid_seeds.csv",
]


@pytest.mark.parametrize("name", SUMMARIES)
def test_summary_provenance(name: str) -> None:
    """P16.6 (#97, S16): every summary record carries one clean fd_commit."""
    df = pd.read_csv(RECORDS / name)
    for col in ("fd_version", "fd_commit", "ws3_version"):
        assert col in df.columns, f"{name} lacks {col}"
    commits = set(df["fd_commit"].astype(str))
    assert len(commits) == 1, commits
    assert not next(iter(commits)).endswith("+dirty")


def _occ(s: pd.Series) -> pd.Series:
    return s.astype(str) == "True"


def test_institution_control_reproduces_core_grid() -> None:
    """The rolling/reset institution is the core design: identical to grid.csv."""
    keys = ["landbase", "discount_rate", "flow_policy"]
    core = pd.read_csv(RECORDS / "grid.csv")
    inst = pd.read_csv(RECORDS / "grid_institutions.csv")
    ctl = inst[(inst["horizon_institution"] == "rolling") & (inst["flow_history"] == "reset")]
    m = core.merge(ctl, on=keys, suffixes=("_core", "_ctl"))
    assert len(m) == len(core) == 432
    assert np.allclose(m["mean_abs_rel_deviation_core"], m["mean_abs_rel_deviation_ctl"], rtol=1e-9)
    assert (_occ(m["occurrence_core"]) == _occ(m["occurrence_ctl"])).all()


def test_seed_42_reproduces_core_grid() -> None:
    """Seed 42 is the tracked draw of landbases 11-18."""
    keys = ["landbase", "discount_rate", "flow_policy"]
    core = pd.read_csv(RECORDS / "grid.csv")
    seeds = pd.read_csv(RECORDS / "grid_seeds.csv")
    m = seeds[seeds["landbase_seed"] == 42].merge(core, on=keys, suffixes=("_s", "_c"))
    assert len(m) == 8 * 4 * 6
    assert np.allclose(m["mean_abs_rel_deviation_s"], m["mean_abs_rel_deviation_c"], rtol=1e-9)


def test_exact_tail_has_no_on_plan_relaxation() -> None:
    """P16.2 (#93, S03): under fixed horizon + carried history (the exact tail
    problem), a material relaxation of the carried anchor may only occur after
    the realized path has left the plan (Bellman's principle)."""
    from fresh_daugherty.replan import is_material_relaxation

    g = pd.read_csv(RECORDS / "grid_institutions_gaps.csv")
    g = g[(g["horizon_institution"] == "fixed") & (g["flow_history"] == "carried")]
    keys = ["landbase", "discount_rate", "flow_policy"]
    bad = []
    for k, cell in g.groupby(keys):
        cell = cell.sort_values("period")
        dev = (cell["realized"] - cell["announced"]).abs() / cell["announced"].abs().clip(lower=1.0)
        prior = dev.cummax().shift(1, fill_value=0.0)
        for (_, row), p in zip(cell.iterrows(), prior, strict=True):
            if is_material_relaxation(str(row["solver_note"])) and p <= 1e-3:
                bad.append((*k, int(row["period"]), float(p)))
    assert not bad, bad[:10]


@pytest.mark.parametrize(
    "name",
    [
        "grid_institutions_gaps.csv",
        "grid_cap_search_gaps.csv",
        "grid_discount_paths_gaps.csv",
        "grid_value_flow_gaps.csv",
        "grid_rolling_mean_gaps.csv",
    ],
)
def test_no_negative_objective_gaps(name: str) -> None:
    """P16.1 (#92, S01/S02): the tail-fixed problem restricts the free one, so
    no recorded objective gap is materially negative."""
    g = pd.read_csv(RECORDS / name).dropna(subset=["objective_gap"])
    bad = g[g["objective_gap"] < -1e-5 * g["obj_free"].abs().clip(lower=1.0)]
    assert bad.empty, bad.head()


PER_PERIOD = [
    "grid_trajectories.csv",
    "grid_discount_paths_trajectories.csv",
    "grid_discount_paths_gaps.csv",
    "grid_cap_search_trajectories.csv",
    "grid_cap_search_gaps.csv",
    "grid_value_flow_trajectories.csv",
    "grid_value_flow_gaps.csv",
    "grid_rolling_mean_trajectories.csv",
    "grid_rolling_mean_gaps.csv",
    "grid_institutions_trajectories.csv",
    "grid_institutions_gaps.csv",
    "grid_seeds_trajectories.csv",
]


@pytest.mark.parametrize("name", PER_PERIOD)
def test_per_period_provenance_matches_summary(name: str) -> None:
    """P17.3 (#104, review T30): per-period records carry the same clean
    fd_commit as their summary."""
    df = pd.read_csv(RECORDS / name)
    summary = name.replace("_trajectories", "").replace("_gaps", "")
    commits = set(df["fd_commit"].astype(str))
    assert commits == set(pd.read_csv(RECORDS / summary)["fd_commit"].astype(str)), commits


@pytest.mark.parametrize("name", SUMMARIES)
def test_thesis_window_metrics_recorded(name: str) -> None:
    """P17.4 (#105): every summary carries the periods 2-11 metrics."""
    df = pd.read_csv(RECORDS / name)
    for col in (
        "mean_abs_rel_deviation_2_11",
        "occurrence_2_11",
        "thesis_volume_inconsistency_2_11",
    ):
        assert col in df.columns, f"{name} lacks {col}"
