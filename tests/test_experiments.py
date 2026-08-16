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
    df = run_policy_grid(
        landbases=(1,),
        discount_rates=(0.04,),
        policies=(pol["NHF"], pol["NDY"]),
        horizon=6,
        workdir=tmp_path,
    )
    assert set(df["flow_policy"]) == {"NHF", "NDY"}
    assert "occurrence" in df.columns
    nhf = df[df["flow_policy"] == "NHF"].iloc[0]
    ndy = df[df["flow_policy"] == "NDY"].iloc[0]
    # No flow constraint -> the problem decomposes -> open-loop == sequential.
    assert nhf["mean_abs_rel_deviation"] < 0.01
    assert nhf["occurrence"] is False or nhf["occurrence"] == False  # noqa: E712
    # NDY on the all-mature landbase is strongly inconsistent.
    assert ndy["mean_abs_rel_deviation"] > 0.05
    assert ndy["occurrence"] == True  # noqa: E712


def test_flow_tolerance_changes_projection(tmp_path: Path) -> None:
    # A looser even-flow band allows a less-uniform projected harvest path.
    tight = run_experiment(
        landbase=1, discount_rate=0.04, flow_tolerance=0.01, horizon=6, workdir=tmp_path / "t"
    )
    loose = run_experiment(
        landbase=1, discount_rate=0.04, flow_tolerance=0.30, horizon=6, workdir=tmp_path / "l"
    )
    assert list(tight.projected) != list(loose.projected)
