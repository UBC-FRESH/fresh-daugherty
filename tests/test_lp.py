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
    """The over-mature timber is harvested over the horizon (harvest occurs)."""
    _, _, df = solved
    # The mature pulse is harvested (positive harvest volume across the horizon).
    assert df["harvest_volume_mcf"].sum() > 0
    # And the forest is converted (growing stock changes as over-mature timber
    # is harvested and the managed forest grows).
    gs = df["growing_stock_mcf"].to_numpy()
    assert gs[-1] != gs[0]


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


def _solve_path(tmp_path, path, horizon=8):
    areas = landbase_areas(1)
    build_woodstock_sections(tmp_path / "model", areas=areas)
    model = prepare_optimization(
        bootstrap_model(tmp_path / "model", horizon=horizon), horizon=horizon
    )
    problem = add_open_loop_problem(
        model, discount_path=path, flow_geometry="consecutive", flow_decrease=0.0
    )
    df = solve_open_loop(model, problem)
    return problem, df["harvest_volume_mcf"].to_numpy()


def test_constant_discount_path_is_bit_identical_to_scalar(tmp_path) -> None:
    """P9.2 regression (issue #54): a constant path must reproduce the scalar
    ``discount_rate`` entry point exactly (objective and optimal plan)."""
    from fresh_daugherty.instance.discount import constant_path

    p_scalar, v_scalar = _solve_rate(tmp_path / "s", 0.04)
    p_path, v_path = _solve_path(tmp_path / "p", constant_path(0.04))
    assert p_scalar.status() == p_path.status() == "optimal"
    assert p_scalar.z() == p_path.z()
    assert (abs(v_scalar - v_path) < 1e-9).all()


def test_declining_discount_path_changes_plan(tmp_path) -> None:
    """A declining rate weights the tail more heavily, so the optimal plan
    shifts relative to the constant-rate control at the same initial rate."""
    from fresh_daugherty.instance.discount import discount_path

    _, v_const = _solve_rate(tmp_path / "c", 0.04)
    _, v_invj = _solve_path(tmp_path / "j", discount_path("invj-4pc-k1"))
    assert not (abs(v_const - v_invj) < 1e-6).all()


def _solve_cap(tmp_path, cap, horizon=10):
    areas = landbase_areas(1)
    build_woodstock_sections(tmp_path / "model", areas=areas)
    model = prepare_optimization(
        bootstrap_model(tmp_path / "model", horizon=horizon), horizon=horizon
    )
    problem = add_open_loop_problem(model, target_flow_mcf=cap)
    df = solve_open_loop(model, problem)
    return problem, df["harvest_volume_mcf"].to_numpy()


def test_loose_cap_matches_unconstrained(tmp_path) -> None:
    """P10.1 (issue #57): a cap above the unconstrained maximum harvest leaves
    the no-flow (NHF) solution unchanged."""
    p_nhf, v_nhf = _solve_geometry(tmp_path / "n", "none")
    p_cap, v_cap = _solve_cap(tmp_path / "c", cap=float(v_nhf.max()) * 2.0)
    assert p_nhf.status() == p_cap.status() == "optimal"
    assert p_nhf.z() == p_cap.z()
    assert (abs(v_nhf - v_cap) < 1e-9).all()


def test_tight_cap_binds_and_stays_feasible(tmp_path) -> None:
    """A tight cap is respected in every period, and the cap-only problem stays
    feasible (lb=0: harvesting nothing is always allowed)."""
    _, v_nhf = _solve_geometry(tmp_path / "n", "none")
    cap = float(v_nhf.max()) * 0.5
    problem, v_cap = _solve_cap(tmp_path / "c", cap)
    assert problem.status() == "optimal"
    assert (v_cap <= cap + 1e-3).all()
    # The cap binds: the capped plan harvests less than the unconstrained peak.
    assert v_cap.max() < v_nhf.max()


class _CaptureModel:
    """Minimal stand-in recording what ``add_open_loop_problem`` passes to ws3."""

    period_length = 10
    periods = (1, 2, 3)

    def __init__(self) -> None:
        self.dtypes: dict = {}
        self.kw: dict = {}

    def nthemes(self) -> int:
        return 5

    def add_problem(self, **kw):
        self.kw = kw
        return object()


def _period1_bounds(**kw) -> tuple[float | None, float | None]:
    m = _CaptureModel()
    add_open_loop_problem(m, **kw)
    hv = (m.kw["cgen_data"] or {}).get("cflw_hv", {})
    return hv.get("lb", {}).get(1), hv.get("ub", {}).get(1)


def test_tail_fixed_band_intersects_carried_anchor() -> None:
    """P16.1 (#92, S01): the gap diagnostic's period-1 band must be intersected
    with the carried flow anchor, not overwrite it (or be overwritten)."""
    from fresh_daugherty.lp import HISTORY_RTOL

    flow = {"flow_geometry": "consecutive", "flow_decrease": 0.1, "flow_increase": 0.1}
    free = _period1_bounds(prev_harvest_mcf=10000.0, **flow)
    fixed = _period1_bounds(prev_harvest_mcf=10000.0, fix_period1_harvest_mcf=9500.0, **flow)
    assert free == pytest.approx((9000.0 * (1 - HISTORY_RTOL), 11000.0 * (1 + HISTORY_RTOL)))
    assert fixed == pytest.approx((9500.0 * 0.99, 9500.0 * 1.01))
    assert fixed != free
    # Announced value outside the carried range: the intersection is empty
    # (lb > ub), so the tail-fixed problem is infeasible, as it should be.
    lb, ub = _period1_bounds(prev_harvest_mcf=10000.0, fix_period1_harvest_mcf=8000.0, **flow)
    assert lb > ub


def test_tail_fixed_band_respects_cap() -> None:
    """P16.1 (#92, S02): in E2 the band must not lift the cap."""
    lb, ub = _period1_bounds(target_flow_mcf=9400.0, fix_period1_harvest_mcf=9400.0)
    assert ub == pytest.approx(9400.0)
    assert lb == pytest.approx(9400.0 * 0.99)


def test_carried_history_requires_volume_denominator() -> None:
    """P16.1 (#92): the carried anchor bounds volume; a revenue-denominated
    policy must not silently get a volume anchor."""
    with pytest.raises(ValueError, match="volume-denominated"):
        _period1_bounds(
            flow_geometry="consecutive",
            flow_decrease=0.0,
            flow_denominator="revenue",
            prev_harvest_mcf=10000.0,
        )


def test_each_mature_type_has_its_own_yield_in_the_built_model(tmp_path) -> None:
    """P16.8 (#99): the two CH-CW mature types (sawtimber, two-storied) shared a
    development-type key, so the built model gave two-storied stands the
    sawtimber volume (10.27 vs 4.66 MCF/ac). Check the *built* model, not the
    back-computed volumes: one DT per Table 5.4 type, each with its own yield."""
    from fresh_daugherty.instance.feis import real_ecoclass_net_revenue
    from fresh_daugherty.instance.thesis import MATURE_TYPE_PNV
    from fresh_daugherty.model import ecoclass_code, mature_rx, mature_volume_mcf

    build_woodstock_sections(tmp_path / "m", areas=landbase_areas(1))
    model = bootstrap_model(tmp_path / "m", horizon=3)
    existing = {k: dt for k, dt in model.dtypes.items() if k[3] == "existing"}
    assert len(existing) == len(MATURE_TYPE_PNV)
    for mt in MATURE_TYPE_PNV:
        key = ("umpqua", ecoclass_code(mt.ecoclass).lower(), mature_rx(mt), "existing", "baseline")
        expected = mature_volume_mcf(mt, real_ecoclass_net_revenue(mt.ecoclass))
        got = existing[key].ycomp("totvol")[mt.age_yr]
        assert got == pytest.approx(expected, rel=1e-6), (mt.vegetation_type, got, expected)


def test_mature_volumes_reproduce_table_5_4_in_the_lp_convention() -> None:
    """P17.2 (#103, review T02): the model's own discounted value (4%, price
    escalation, end-of-period discounting) of harvesting each mature type in
    period 1 equals Table 5.4; before, volumes ignored discounting and the LP
    valued the stands at 0.746 x Table 5.4. Period 2 is not forced (flat
    volumes); it stays within 15% of Table 5.4."""
    from fresh_daugherty.model import mature_value_check

    df = mature_value_check()
    p1 = df[df["period"] == 1]
    assert p1["ratio"].to_numpy() == pytest.approx(1.0, rel=1e-9)
    p2 = df[df["period"] == 2]
    assert p2["ratio"].between(0.85, 1.16).all()


def test_mature_calibration_uses_the_lp_value_convention() -> None:
    """The calibration factor is the LP's own: the period-1 discount factor of
    the 4% constant path times the price escalation at the end of period 1."""
    from fresh_daugherty.instance.discount import constant_path
    from fresh_daugherty.lp import _escalated
    from fresh_daugherty.model import MATURE_PERIOD1_VALUE_FACTOR

    lp_factor = constant_path(0.04).factors(horizon=1)[0] * _escalated(1.0, 10)
    assert lp_factor == pytest.approx(MATURE_PERIOD1_VALUE_FACTOR, rel=1e-12)
