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


def test_flow_tolerance_changes_projection(tmp_path: Path) -> None:
    # A looser even-flow band allows a less-uniform projected harvest path.
    tight = run_experiment(
        landbase=1, discount_rate=0.04, flow_tolerance=0.01, horizon=6, workdir=tmp_path / "t"
    )
    loose = run_experiment(
        landbase=1, discount_rate=0.04, flow_tolerance=0.30, horizon=6, workdir=tmp_path / "l"
    )
    assert list(tight.projected) != list(loose.projected)
