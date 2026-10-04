"""Tests for the case-study experiments grid (P4)."""

from __future__ import annotations

from pathlib import Path

import pytest

from fresh_daugherty.experiments import run_experiment, run_experiment_grid
from fresh_daugherty.instance.reconstruct import calibrate


@pytest.fixture(scope="module", autouse=True)
def _warm_calibration() -> None:
    calibrate()


def test_run_experiment_produces_inconsistency(tmp_path: Path) -> None:
    result = run_experiment(
        landbase=1,
        discount_rate=0.04,
        flow_tolerance=0.05,
        horizon=6,
        workdir=tmp_path,
    )
    assert result.landbase == 1
    assert len(result.projected) == 6
    assert len(result.realized) == 6
    # The open-loop plan's tail is not followed.
    assert result.metrics["mean_abs_rel_deviation"] > 0.05


def test_experiment_grid_shape(tmp_path: Path) -> None:
    df = run_experiment_grid(
        landbases=(1, 2),
        discount_rates=(0.04,),
        flow_tolerances=(0.05,),
        horizon=5,
        workdir=tmp_path,
    )
    assert len(df) == 2
    assert set(df["landbase"]) == {1, 2}
    assert (df["mean_abs_rel_deviation"] >= 0).all()
    # The occurrence criterion flows through to the grid output.
    assert "occurrence" in df.columns
    assert df["occurrence"].dtype == bool


def test_flow_kwargs_for_policy_mapping() -> None:
    """Table 5.6 policies map to the correct flow-constraint geometry."""
    from fresh_daugherty.instance.thesis import HARVEST_FLOW_POLICIES
    from fresh_daugherty.lp import flow_kwargs_for_policy

    pol = {p.code: p for p in HARVEST_FLOW_POLICIES}
    assert flow_kwargs_for_policy(pol["NHF"]) == {"flow_geometry": "none"}
    assert flow_kwargs_for_policy(pol["NDY"]) == {
        "flow_geometry": "consecutive",
        "flow_decrease": 0.0,
        "flow_increase": None,
    }
    assert flow_kwargs_for_policy(pol["+/-10%"]) == {
        "flow_geometry": "consecutive",
        "flow_decrease": 0.10,
        "flow_increase": 0.10,
    }


def test_policy_grid_occurrence_and_nhf_baseline(tmp_path: Path) -> None:
    """Policy grid runs; NHF (no flow) is consistent, NDY is inconsistent."""
    from fresh_daugherty.experiments import run_policy_grid
    from fresh_daugherty.instance.thesis import HARVEST_FLOW_POLICIES

    pol = {p.code: p for p in HARVEST_FLOW_POLICIES}
    df, trajectories = run_policy_grid(
        landbases=(1,),
        discount_rates=(0.04,),
        policies=(pol["NHF"], pol["NDY"]),
        horizon=6,
        workdir=tmp_path,
    )
    assert set(df["flow_policy"]) == {"NHF", "NDY"}
    assert "occurrence" in df.columns
    # The trajectories frame carries the full per-cell projected/realized record.
    assert {"landbase", "flow_policy", "period", "projected_mcf", "realized_mcf"} <= set(
        trajectories.columns
    )
    nhf = df[df["flow_policy"] == "NHF"].iloc[0]
    ndy = df[df["flow_policy"] == "NDY"].iloc[0]
    # No flow constraint -> the problem decomposes -> open-loop == sequential.
    assert nhf["mean_abs_rel_deviation"] < 0.01
    assert nhf["occurrence"] is False or nhf["occurrence"] == False  # noqa: E712
    # NDY on the all-mature landbase is strongly inconsistent.
    assert ndy["mean_abs_rel_deviation"] > 0.05
    assert ndy["occurrence"] == True  # noqa: E712
    # P14.2 (#77): the realized period-1 harvest is the open-loop period-1 decision.
    _assert_period1_invariant(trajectories)


def test_flow_tolerance_changes_projection(tmp_path: Path) -> None:
    # A looser even-flow band allows a less-uniform projected harvest path.
    tight = run_experiment(
        landbase=1, discount_rate=0.04, flow_tolerance=0.01, horizon=6, workdir=tmp_path / "t"
    )
    loose = run_experiment(
        landbase=1, discount_rate=0.04, flow_tolerance=0.30, horizon=6, workdir=tmp_path / "l"
    )
    assert list(tight.projected) != list(loose.projected)


def test_discount_path_grid_smoke(tmp_path: Path) -> None:
    """P9.3 (issue #55): the E1 discount-path grid runs end to end and every
    cell carries metrics, trajectories, and gap-diagnostic records."""
    from fresh_daugherty.experiments import run_discount_path_grid
    from fresh_daugherty.instance.discount import discount_path
    from fresh_daugherty.instance.thesis import HARVEST_FLOW_POLICIES

    pol = {p.code: p for p in HARVEST_FLOW_POLICIES}
    summary, trajectories, gaps = run_discount_path_grid(
        landbases=(1,),
        discount_paths=(discount_path("linear-4pc-0pc"),),
        policies=(pol["NDY"],),
        horizon=5,
        workdir=tmp_path,
    )
    assert len(summary) == 1
    row = summary.iloc[0]
    assert row["discount_path"] == "linear-4pc-0pc"
    assert row["path_family"] == "linear"
    assert row["discount_rate"] == 0.04
    # Provenance columns are populated.
    assert row["fd_version"] and row["ws3_version"]
    # Per-period records: horizon rows in each long-format frame.
    assert len(trajectories) == len(gaps) == 5
    assert {"period", "projected_mcf", "realized_mcf"} <= set(trajectories.columns)
    assert {"period", "announced", "realized", "objective_gap", "tail_status"} <= set(gaps.columns)
    # NDY on the all-mature landbase is strongly inconsistent under the path too.
    assert row["mean_abs_rel_deviation"] > 0.05
    # P14.2 (#77): period-1 invariant and commit-level provenance.
    _assert_period1_invariant(trajectories)
    assert row["fd_commit"]


def _assert_period1_invariant(trajectories) -> None:
    """Period-1 announced equals period-1 realized in every cell (P14.2, #77)."""
    import numpy as np

    first = trajectories[trajectories["period"] == 1]
    assert len(first) > 0
    assert np.allclose(first["projected_mcf"], first["realized_mcf"], rtol=1e-6, atol=1e-6)


def test_rolling_mean_grid_smoke(tmp_path: Path) -> None:
    """P14.2 (#77): the E4 rolling-mean grid runs end to end for both anchoring
    readings, keeps the period-1 invariant, and records commit provenance."""
    from fresh_daugherty.experiments import run_rolling_mean_grid

    summary, trajectories, gaps = run_rolling_mean_grid(
        landbases=(1,),
        discount_rates=(0.04,),
        windows=(2,),
        readings=(False, True),
        horizon=5,
        workdir=tmp_path,
    )
    assert len(summary) == 2
    assert summary["fd_commit"].astype(bool).all()
    assert len(trajectories) == len(gaps) == 10
    _assert_period1_invariant(trajectories)


def test_institution_grid_smoke(tmp_path: Path) -> None:
    """P15.2 (#84): the institution grid runs all four (horizon, flow history)
    institutions with gap records and provenance; the fixed/carried cell
    reproduces the open-loop plan (null test) and the rolling/reset cell is the
    core institution."""
    from fresh_daugherty.experiments import INSTITUTIONS, run_institution_grid
    from fresh_daugherty.instance.thesis import HARVEST_FLOW_POLICIES

    pol = {p.code: p for p in HARVEST_FLOW_POLICIES}
    summary, trajectories, gaps = run_institution_grid(
        landbases=(1,),
        discount_rates=(0.04,),
        policies=(pol["NDY"],),
        institutions=INSTITUTIONS,
        horizon=6,
        workdir=tmp_path,
    )
    assert len(summary) == 4 and len(trajectories) == len(gaps) == 24
    assert summary["fd_commit"].astype(bool).all()
    _assert_period1_invariant(trajectories)
    null = summary[(summary.horizon_institution == "fixed") & (summary.flow_history == "carried")]
    assert null["mean_abs_rel_deviation"].iloc[0] < 1e-4
    assert null["relax_share"].iloc[0] == 0.0


def test_cap_search_grid_smoke(tmp_path: Path) -> None:
    """P15.5 (#87): the E2 cap-search grid runs end to end at a non-default
    rate, keeps the period-1 invariant, records commit provenance, and its gap
    records carry revenue (for the NPV comparison with realized NDY)."""
    import numpy as np

    from fresh_daugherty.experiments import run_cap_search_grid

    summary, trajectories, gaps = run_cap_search_grid(
        landbases=(1,), discount_rates=(0.02,), horizon=5, workdir=tmp_path
    )
    assert len(summary) == 1 and bool(summary["converged"].iloc[0])
    assert summary["fd_commit"].astype(bool).all()
    _assert_period1_invariant(trajectories)
    assert {"announced_revenue", "realized_revenue"} <= set(gaps.columns)
    assert np.isfinite(gaps["realized_revenue"]).all()
