"""Tests for the case-study ws3 model and open-loop LP (P1.2)."""

from __future__ import annotations

import pytest

from fresh_daugherty.instance.landbases import landbase_areas
from fresh_daugherty.lp import add_open_loop_problem, solve_open_loop
from fresh_daugherty.model import (
    bootstrap_model,
    build_woodstock_sections,
    prepare_optimization,
)


@pytest.fixture(scope="module")
def solved(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("model")
    areas = landbase_areas(1)
    build_woodstock_sections(tmp / "model", areas=areas)
    model = prepare_optimization(bootstrap_model(tmp / "model", horizon=15), horizon=15)
    problem = add_open_loop_problem(model)
    df = solve_open_loop(model, problem)
    return model, problem, df


def test_model_builds_with_five_themes(solved) -> None:
    model, _, _ = solved
    assert model.nthemes() == 5
    assert len(model.dtypes) > 0


def test_open_loop_solves_optimal(solved) -> None:
    _, problem, _ = solved
    assert problem.status() == "optimal"


def test_even_flow_holds(solved) -> None:
    """Harvest volume per period stays within the 5% even-flow band of period 1."""
    _, _, df = solved
    v = df["harvest_volume_mcf"].to_numpy()
    assert v[0] > 0
    for x in v[1:]:
        assert abs(x - v[0]) <= 0.05 * v[0] + 1e-6


def test_mature_timber_is_drawn_down(solved) -> None:
    """Growing stock declines as the over-mature timber is harvested."""
    _, _, df = solved
    gs = df["growing_stock_mcf"].to_numpy()
    assert gs[-1] < gs[0]


def test_landbase_area_conserved_initially() -> None:
    areas = landbase_areas(1)
    assert areas["area_ac"].sum() == pytest.approx(10_000.0)
    areas2 = landbase_areas(2)
    assert areas2["area_ac"].sum() == pytest.approx(10_000.0)
    # Landbase 2 excludes CM-CE.
    assert "CMCE" not in set(areas2["ecoclass"])


def _solve_geometry(tmp_path, flow_geometry, **kw):
    areas = landbase_areas(1)
    build_woodstock_sections(tmp_path / "model", areas=areas)
    model = prepare_optimization(bootstrap_model(tmp_path / "model", horizon=10), horizon=10)
    problem = add_open_loop_problem(model, flow_geometry=flow_geometry, **kw)
    df = solve_open_loop(model, problem)
    return problem, df["harvest_volume_mcf"].to_numpy()


def test_consecutive_ndy_is_nondeclining(tmp_path) -> None:
    """Consecutive-period NDY (max_decrease=0): harvest never declines period over period."""
    problem, v = _solve_geometry(tmp_path, "consecutive", flow_decrease=0.0)
    assert problem.status() == "optimal"
    for k in range(1, len(v)):
        assert v[k] >= v[k - 1] - 1e-3


def test_consecutive_bounded_deviation_band_holds(tmp_path) -> None:
    """Consecutive +/-eps: each period's harvest is within eps of the previous."""
    eps = 0.10
    problem, v = _solve_geometry(tmp_path, "consecutive", flow_decrease=eps, flow_increase=eps)
    assert problem.status() == "optimal"
    for k in range(1, len(v)):
        assert v[k] <= (1.0 + eps) * v[k - 1] + 1e-3
        assert v[k] >= (1.0 - eps) * v[k - 1] - 1e-3


def test_consecutive_geometry_differs_from_period1(tmp_path) -> None:
    """The consecutive-period geometry is a different constraint than the period-1 band."""
    _, v_consec = _solve_geometry(tmp_path / "c", "consecutive", flow_decrease=0.0)
    _, v_p1 = _solve_geometry(tmp_path / "p", "period1", flow_coefficient=0.05)
    assert not (abs(v_consec - v_p1) < 1e-6).all()


def _solve_rate(tmp_path, rate, horizon=8):
    areas = landbase_areas(1)
    build_woodstock_sections(tmp_path / "model", areas=areas)
    model = prepare_optimization(
        bootstrap_model(tmp_path / "model", horizon=horizon), horizon=horizon
    )
    problem = add_open_loop_problem(
        model, discount_rate=rate, flow_geometry="consecutive", flow_decrease=0.0
    )
    df = solve_open_loop(model, problem)
    return problem, df["harvest_volume_mcf"].to_numpy()


def test_objective_is_nonzero_and_rate_dependent(tmp_path) -> None:
    """Regression (the inert-objective bug): the NPV objective must be nonzero and
    the optimal plan must depend on the discount rate (the thesis's rate effect)."""
    p0, v0 = _solve_rate(tmp_path / "r0", 0.0)
    p6, v6 = _solve_rate(tmp_path / "r6", 0.06)
    # The objective must actually value the harvest (the ws3 theme-lowercasing bug
    # had silently zeroed every objective coefficient).
    assert any(abs(c) > 1e-9 for c in p0._z.values())
    assert p0.z() > 0
    # The chosen plan differs across rates (0% back-loads; 6% flattens under NDY).
    assert not (abs(v0 - v6) < 1e-6).all()
    # Objective value decreases as the discount rate rises (discounting bites).
    assert p6.z() < p0.z()
