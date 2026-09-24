"""Tests for the E3 value-denominated flow constraints (P11.1, issue #61)."""

from __future__ import annotations

import pytest

from fresh_daugherty.instance.landbases import landbase_areas
from fresh_daugherty.lp import add_open_loop_problem, solve_open_loop
from fresh_daugherty.model import (
    bootstrap_model,
    build_woodstock_sections,
    prepare_optimization,
)


def _solve(tmp_path, *, denominator="volume", horizon=10, **kw):
    areas = landbase_areas(1)
    build_woodstock_sections(tmp_path / "model", areas=areas)
    model = prepare_optimization(
        bootstrap_model(tmp_path / "model", horizon=horizon), horizon=horizon
    )
    problem = add_open_loop_problem(model, flow_denominator=denominator, **kw)
    df = solve_open_loop(model, problem)
    return model, problem, df


def test_volume_denominator_is_bit_identical_to_default(tmp_path) -> None:
    """Regression: flow_denominator='volume' reproduces the default exactly."""
    _, p_def, df_def = _solve(tmp_path / "d", flow_geometry="consecutive", flow_decrease=0.0)
    _, p_vol, df_vol = _solve(
        tmp_path / "v", denominator="volume", flow_geometry="consecutive", flow_decrease=0.0
    )
    assert p_def.status() == p_vol.status() == "optimal"
    assert p_def.z() == p_vol.z()
    assert (abs(df_def["harvest_volume_mcf"] - df_vol["harvest_volume_mcf"]) < 1e-9).all()


def test_revenue_ndy_is_nondeclining_in_revenue(tmp_path) -> None:
    """Under revenue NDY the *revenue* trajectory never declines period over
    period (the constraint links R_n, not volume)."""
    from fresh_daugherty.instance.thesis import PERIOD_LENGTH_YEARS
    from fresh_daugherty.lp import _ecoclass_economics, _escalated

    model, problem, _df = _solve(
        tmp_path, denominator="revenue", flow_geometry="consecutive", flow_decrease=0.0
    )
    assert problem.status() == "optimal"
    # Reconstruct the per-period revenue trajectory from the solved model:
    # sum over ecoclasses of harvested volume x escalated net price.
    econ = _ecoclass_economics()
    dtks_by_eco: dict[str, list] = {}
    for dtk in model.dtypes:
        dtks_by_eco.setdefault(str(dtk[1]).lower(), []).append(dtk)
    revenue = []
    for p in model.periods:
        total = 0.0
        for code, (price, hcost) in econ.items():
            vol = sum(
                model.compile_product(p, "totvol", acode="harvest", dtype_keys=[dtk])
                for dtk in dtks_by_eco.get(code, [])
            )
            total += vol * (_escalated(price, p * PERIOD_LENGTH_YEARS) - hcost)
        revenue.append(total)
    for k in range(1, len(revenue)):
        assert revenue[k] >= revenue[k - 1] - 1e-3


def test_revenue_denominator_changes_solution(tmp_path) -> None:
    """The revenue-denominated NDY picks a different plan than volume NDY."""
    _, _, df_vol = _solve(tmp_path / "v", flow_geometry="consecutive", flow_decrease=0.0)
    _, _, df_rev = _solve(
        tmp_path / "r", denominator="revenue", flow_geometry="consecutive", flow_decrease=0.0
    )
    v = df_vol["harvest_volume_mcf"].to_numpy()
    r = df_rev["harvest_volume_mcf"].to_numpy()
    assert not (abs(v - r) < 1e-6).all()


def test_invalid_denominator_raises(tmp_path) -> None:
    areas = landbase_areas(1)
    build_woodstock_sections(tmp_path / "model", areas=areas)
    model = prepare_optimization(bootstrap_model(tmp_path / "model", horizon=5), horizon=5)
    with pytest.raises(ValueError, match="flow_denominator"):
        add_open_loop_problem(model, flow_denominator="dubloons")
