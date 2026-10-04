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


def test_gap_replan_collects_revenue(tmp_path) -> None:
    """P11.2 (issue #62): the gap diagnostic can collect the announced/realized
    revenue trajectories, and revenue divergence is scorable with the standard
    metric."""
    import numpy as np

    from fresh_daugherty.replan import consistency_gap_replan, inconsistency_metrics

    areas = landbase_areas(1)
    build_woodstock_sections(tmp_path / "model", areas=areas)
    model = prepare_optimization(bootstrap_model(tmp_path / "model", horizon=5), horizon=5)
    df = consistency_gap_replan(
        model,
        workdir=tmp_path / "gap",
        discount_rate=0.04,
        flow_geometry="consecutive",
        flow_decrease=0.0,
        collect_revenue=True,
    )
    assert {"announced", "realized", "announced_revenue", "realized_revenue"} <= set(df.columns)
    assert np.isfinite(df["announced_revenue"]).all()
    assert np.isfinite(df["realized_revenue"]).all()
    # Period-1 announced revenue equals realized revenue (consistent by construction).
    assert df["announced_revenue"].iloc[0] == pytest.approx(df["realized_revenue"].iloc[0])
    # Revenue divergence is scorable with the standard metric.
    m = inconsistency_metrics(list(df["announced_revenue"]), list(df["realized_revenue"]))
    assert 0.0 <= m["mean_abs_rel_deviation"] <= 1.0
    # And the volume record is unaffected by the revenue columns.
    assert {"objective_gap", "tail_status"} <= set(df.columns)


def test_gap_replan_announces_the_revenue_plan(tmp_path) -> None:
    """P14.1 (issue #76) regression: under ``flow_denominator="revenue"`` the
    announced (period-0 open-loop) trajectory must be the *revenue*-denominated
    plan. At 8cf2aa8, which produced the original E3 records,
    ``consistency_gap_replan`` called ``open_loop_projection`` without
    ``flow_denominator``, so every revenue cell announced the volume plan and
    period-1 announced != realized. (Fixed incidentally in e72ab2b, P12.2.)"""
    from fresh_daugherty.replan import consistency_gap_replan, open_loop_projection

    horizon = 5
    flow = {"flow_geometry": "consecutive", "flow_decrease": 0.0}

    def fresh(name):
        build_woodstock_sections(tmp_path / name, areas=landbase_areas(1))
        model = bootstrap_model(tmp_path / name, horizon=horizon)
        return prepare_optimization(model, horizon=horizon)

    df = consistency_gap_replan(
        fresh("gap"),
        workdir=tmp_path / "gapwork",
        discount_rate=0.04,
        flow_denominator="revenue",
        collect_revenue=True,
        **flow,
    )
    revenue_plan = open_loop_projection(
        fresh("rev"), discount_rate=0.04, flow_denominator="revenue", **flow
    )
    volume_plan = open_loop_projection(
        fresh("vol"), discount_rate=0.04, flow_denominator="volume", **flow
    )
    announced = list(df["announced"])
    # Sensitivity: on landbase 1 the two denominators give different plans,
    # so the checks below can tell them apart.
    assert announced != pytest.approx(volume_plan, rel=1e-6)
    # The announced trajectory is the revenue-denominated open-loop plan ...
    assert announced == pytest.approx(revenue_plan, rel=1e-9)
    # ... and the simulator invariant holds: the realized period-1 harvest is
    # the open-loop period-1 decision.
    assert df["announced"].iloc[0] == pytest.approx(df["realized"].iloc[0], rel=1e-9)
