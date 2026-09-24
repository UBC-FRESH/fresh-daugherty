"""Tests for the E4 rolling-mean NDY constraint form (P12.1, issue #64)."""

from __future__ import annotations

import pytest

from fresh_daugherty.instance.landbases import landbase_areas
from fresh_daugherty.lp import add_open_loop_problem, solve_open_loop
from fresh_daugherty.model import (
    bootstrap_model,
    build_woodstock_sections,
    prepare_optimization,
)


def _solve(tmp_path, *, horizon=10, **kw):
    areas = landbase_areas(1)
    build_woodstock_sections(tmp_path / "model", areas=areas)
    model = prepare_optimization(
        bootstrap_model(tmp_path / "model", horizon=horizon), horizon=horizon
    )
    problem = add_open_loop_problem(model, **kw)
    df = solve_open_loop(model, problem)
    return problem, df["harvest_volume_mcf"].to_numpy()


def test_window_1_degenerates_to_pointwise_ndy(tmp_path) -> None:
    """k=1 rolling mean is exactly the pointwise consecutive NDY."""
    p_ndy, v_ndy = _solve(tmp_path / "n", flow_geometry="consecutive", flow_decrease=0.0)
    p_rm, v_rm = _solve(tmp_path / "r", flow_geometry="rolling_mean", flow_window=1)
    assert p_ndy.status() == p_rm.status() == "optimal"
    assert p_ndy.z() == pytest.approx(p_rm.z(), rel=1e-6)
    assert (abs(v_ndy - v_rm) < 1e-3).all()


def test_rolling_mean_window_geometry_holds(tmp_path) -> None:
    """The k=2 solution respects H_t >= mean(H_{t-2}, H_{t-1}) (with the
    partial-window seeding: H_2 >= H_1)."""
    problem, v = _solve(tmp_path, flow_geometry="rolling_mean", flow_window=2)
    assert problem.status() == "optimal"
    assert v[1] >= v[0] - 1e-3  # partial window: H_2 >= H_1
    for t in range(2, len(v)):  # H_t >= mean(H_{t-2}, H_{t-1})
        assert v[t] >= 0.5 * (v[t - 2] + v[t - 1]) - 1e-3


def test_rolling_mean_k2_is_a_relaxation_of_pointwise_ndy(tmp_path) -> None:
    """Any pointwise-NDY-feasible plan is rolling-mean-feasible (if
    H_t >= H_{t-1} then H_t >= the window mean), so the k=2 rolling mean's
    optimum is at least the NDY optimum (they coincide on landbase 1, where
    the level plan is optimal under both — which also cross-validates the
    row construction)."""
    p_ndy, _ = _solve(tmp_path / "n", flow_geometry="consecutive", flow_decrease=0.0)
    p_rm, _ = _solve(tmp_path / "r", flow_geometry="rolling_mean", flow_window=2)
    assert p_ndy.status() == p_rm.status() == "optimal"
    assert p_rm.z() >= p_ndy.z() - 1e-6


def test_rolling_mean_rows_span_the_window(tmp_path) -> None:
    """Structural difference: the k=2 rolling-mean row for period t mixes
    coefficients from periods {t-2, t-1, t}; the pointwise NDY row mixes only
    {t-1, t} (fewer nonzero coefficients)."""
    areas = landbase_areas(1)
    build_woodstock_sections(tmp_path / "model", areas=areas)
    model = prepare_optimization(bootstrap_model(tmp_path / "model", horizon=6), horizon=6)
    p_ndy = add_open_loop_problem(model, flow_geometry="consecutive", flow_decrease=0.0, name="ndy")
    p_rm = add_open_loop_problem(model, flow_geometry="rolling_mean", flow_window=2, name="rm")
    nz_ndy = sum(abs(v) > 1e-12 for v in p_ndy._constraints["flw-lb_003_cflw_hv"].coeffs.values())
    nz_rm = sum(abs(v) > 1e-12 for v in p_rm._constraints["flw-rm_003_cflw_hv"].coeffs.values())
    assert nz_rm > nz_ndy


def test_rolling_mean_revenue_denominator_runs(tmp_path) -> None:
    """The rolling-mean form composes with the E3 revenue denominator."""
    problem, v = _solve(
        tmp_path,
        flow_geometry="rolling_mean",
        flow_window=2,
        flow_denominator="revenue",
    )
    assert problem.status() == "optimal"
    assert (v >= 0).all()


def test_invalid_window_raises(tmp_path) -> None:
    areas = landbase_areas(1)
    build_woodstock_sections(tmp_path / "model", areas=areas)
    model = prepare_optimization(bootstrap_model(tmp_path / "model", horizon=5), horizon=5)
    with pytest.raises(ValueError, match="flow_window"):
        add_open_loop_problem(model, flow_geometry="rolling_mean", flow_window=0)
