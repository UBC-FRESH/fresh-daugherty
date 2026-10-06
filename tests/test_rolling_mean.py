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


def _replan(tmp_path, *, horizon=6, **kw):
    from fresh_daugherty.replan import sequential_replan

    areas = landbase_areas(1)
    build_woodstock_sections(tmp_path / "model", areas=areas)
    model = prepare_optimization(
        bootstrap_model(tmp_path / "model", horizon=horizon), horizon=horizon
    )
    return sequential_replan(model, workdir=tmp_path / "replan", discount_rate=0.04, **kw)


def test_both_anchoring_readings_run(tmp_path) -> None:
    """P12.2 (issue #65): within-plan and realized-history readings both run
    and produce horizon-length trajectories."""
    for reading in (False, True):
        df = _replan(
            tmp_path / str(reading),
            flow_geometry="rolling_mean",
            flow_window=2,
            rolling_realized_history=reading,
        )
        assert len(df) == 6
        assert (df["harvest_volume_mcf"] >= 0).all()


def test_realized_history_reading_floors_against_realized(tmp_path) -> None:
    """Under the realized-history reading, each replan's period-1 harvest is
    floored at the mean of the previous k REALIZED harvests (unless the solver
    had to relax, which the solver_note column records)."""
    k = 2
    df = _replan(
        tmp_path,
        flow_geometry="rolling_mean",
        flow_window=k,
        rolling_realized_history=True,
        record_solver_notes=True,
    )
    assert "solver_note" in df.columns
    v = list(df["harvest_volume_mcf"])
    notes = list(df["solver_note"])
    # P16.2 (#93): minimal-relaxation ladder; the floor holds up to the
    # recorded loosening unless it was dropped.
    for n in notes:
        assert n in {"ok", "relaxed_floor", "dropped_flow"} or n.startswith("history_rtol="), n
    for t in range(1, len(v)):
        if notes[t] in ("relaxed_floor", "dropped_flow"):
            continue
        rtol = float(notes[t].split("=")[1]) if notes[t].startswith("history_rtol=") else 1e-6
        window = v[max(0, t - k) : t]
        assert v[t] >= (sum(window) / len(window)) * (1 - rtol) * (1 - 1e-6)


@pytest.mark.parametrize(
    ("window", "hist", "expected"),
    [
        # rhs = (1 - rtol) * mean of the realized part of each window
        (2, (100.0, 200.0), {1: (100 + 200) / 2, 2: 200 / 2}),
        (3, (100.0, 200.0, 300.0), {1: 600 / 3, 2: (200 + 300) / 3, 3: 300 / 3}),
    ],
)
def test_realized_history_window_uses_most_recent_harvests(tmp_path, window, hist, expected):
    """P17.1 (#102, review T01): window positions before the plan's present map
    to the realized harvests most recent first (the floor of period 2 under a
    2-window uses the latest realized harvest, not the oldest)."""
    from fresh_daugherty.lp import HISTORY_RTOL, add_open_loop_problem

    build_woodstock_sections(tmp_path / "m", areas=landbase_areas(1))
    model = prepare_optimization(bootstrap_model(tmp_path / "m", horizon=4), horizon=4)
    problem = add_open_loop_problem(
        model, flow_geometry="rolling_mean", flow_window=window, realized_history=hist
    )
    rhs = {
        int(n.split("_")[1]): c.rhs
        for n, c in problem._constraints.items()
        if n.startswith("flw-rm")
    }
    for t, mean_part in expected.items():
        assert rhs[t] == pytest.approx(mean_part * (1 - HISTORY_RTOL)), (t, rhs[t])
