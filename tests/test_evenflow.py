"""Tests for the E2 even-flow metric and cap search (P10.2/P10.3, issues #58-#59)."""

from __future__ import annotations

from pathlib import Path

from fresh_daugherty.evenflow import (
    EvenFlowCriteria,
    assess_even_flow,
    calibrate_even_flow_cap,
)
from fresh_daugherty.instance.landbases import landbase_areas
from fresh_daugherty.model import (
    bootstrap_model,
    build_woodstock_sections,
    prepare_optimization,
)


def test_level_trajectory_is_even() -> None:
    rep = assess_even_flow([1000.0] * 15)
    assert rep.is_even
    assert abs(rep.slope) < 1e-9
    assert rep.cv == 0.0
    assert rep.max_fluctuation == 0.0


def test_trending_trajectory_fails() -> None:
    # A 5%-of-mean per-period decline exceeds the 1% default trend threshold.
    v = [1000.0 - 45.0 * t for t in range(15)]
    rep = assess_even_flow(v)
    assert not rep.is_even
    assert rep.slope < 0
    assert rep.slope_rel > 0.01


def test_oscillating_trajectory_fails_fluctuation() -> None:
    # +/-10% period-over-period swings, zero trend: fails the fluctuation leg.
    v = [1000.0 + (100.0 if t % 2 else -100.0) for t in range(15)]
    rep = assess_even_flow(v)
    assert not rep.is_even
    assert rep.max_fluctuation > 0.05
    assert rep.slope_rel < 0.01


def test_dispersed_trajectory_fails_cv() -> None:
    v = [500.0] * 7 + [1500.0] * 8  # step change: large CV, moderate trend
    rep = assess_even_flow(v, EvenFlowCriteria(max_slope_rel=1.0, max_fluctuation=1.0))
    assert not rep.is_even
    assert rep.cv > 0.05


def test_near_zero_trajectory_is_not_even() -> None:
    assert not assess_even_flow([0.0] * 15).is_even
    assert not assess_even_flow([1e-12] * 15).is_even


def test_custom_thresholds() -> None:
    # Gently trending trajectory passes under loose thresholds, fails under tight.
    v = [1000.0 - 5.0 * t for t in range(15)]
    assert assess_even_flow(v, EvenFlowCriteria(max_slope_rel=0.01, max_cv=0.05)).is_even
    assert not assess_even_flow(v, EvenFlowCriteria(max_slope_rel=0.001, max_cv=0.05)).is_even


def test_cap_search_converges_to_even_realized_flow(tmp_path: Path) -> None:
    """P10.3: the bisection converges on landbase 1 (all-mature, the hard case)
    and the calibrated cap yields an even realized trajectory."""
    workdir = tmp_path / "cap"
    areas = landbase_areas(1)
    build_woodstock_sections(workdir / "model", areas=areas)
    model = prepare_optimization(bootstrap_model(workdir / "model", horizon=6), horizon=6)
    rec = calibrate_even_flow_cap(
        model,
        landbase=1,
        workdir=workdir,
        discount_rate=0.04,
        rel_tol=0.02,  # coarse tolerance for a fast test
    )
    assert rec.converged
    assert rec.calibrated_cap_mcf is not None and rec.calibrated_cap_mcf > 0
    assert rec.realized_report.is_even
    assert rec.iterations <= 25
    assert len(rec.history) == rec.iterations
    assert len(rec.projected) == len(rec.realized) == 6
