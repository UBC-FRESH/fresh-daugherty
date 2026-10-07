"""Tests for the sequential-replanning simulator + inconsistency (P3)."""

from __future__ import annotations

import pytest

from fresh_daugherty.instance.landbases import landbase_areas
from fresh_daugherty.instance.reconstruct import calibrate
from fresh_daugherty.model import bootstrap_model, build_woodstock_sections, prepare_optimization
from fresh_daugherty.replan import (
    inconsistency_metrics,
    open_loop_projection,
    sequential_replan,
)


@pytest.fixture(scope="module")
def replan_result(tmp_path_factory):
    calibrate()  # warm the calibration cache once
    tmp = tmp_path_factory.mktemp("replan")
    areas = landbase_areas(1)
    build_woodstock_sections(tmp / "model", areas=areas)
    # Horizon 10 (was 6): with the thesis's terminal constraints (P18.2) a
    # 6-period horizon is dominated by the final-period rows.
    model = prepare_optimization(bootstrap_model(tmp / "model", horizon=10), horizon=10)
    projected = open_loop_projection(model)
    realized = sequential_replan(model, workdir=tmp / "replans")
    return projected, list(realized["harvest_volume_mcf"])


def test_open_loop_projection_is_even_flow(replan_result) -> None:
    projected, _ = replan_result
    assert projected[0] > 0
    for v in projected[1:]:
        assert abs(v - projected[0]) <= 0.05 * projected[0] + 1e-6


def test_period_one_is_consistent(replan_result) -> None:
    # The immediate (period-1) decision is always followed; inconsistency
    # appears in the tail.
    projected, realized = replan_result
    assert realized[0] == pytest.approx(projected[0], rel=1e-6)


def test_plan_tail_is_not_followed(replan_result) -> None:
    """Dynamic inconsistency: the open-loop plan's tail is not what the
    realized replanned trajectory delivers."""
    projected, realized = replan_result
    m = inconsistency_metrics(projected, realized)
    assert m["mean_abs_rel_deviation"] > 0.10
    # Occurrence criterion: mean relative deviation exceeds the stated threshold.
    assert m["occurrence"] is True
    assert m["occurrence_tolerance"] == pytest.approx(0.05)


def test_occurrence_criterion_threshold() -> None:
    """The occurrence flag follows the stated mean-deviation threshold."""
    p = [100.0, 100.0, 100.0]
    # Small deviation (below threshold): consistent.
    m_ok = inconsistency_metrics(p, [100.0, 99.0, 101.0])
    assert m_ok["mean_abs_rel_deviation"] < m_ok["occurrence_tolerance"]
    assert m_ok["occurrence"] is False
    # Large deviation (above threshold): inconsistent.
    m_bad = inconsistency_metrics(p, [100.0, 50.0, 150.0])
    assert m_bad["mean_abs_rel_deviation"] > m_bad["occurrence_tolerance"]
    assert m_bad["occurrence"] is True
    # A stricter threshold flips the classification of a marginal case.
    m_strict = inconsistency_metrics(p, [100.0, 90.0, 110.0], occurrence_tolerance=0.05)
    assert m_strict["occurrence"] is True


def test_replanning_is_reproducible(tmp_path) -> None:
    calibrate()

    def run():
        areas = landbase_areas(1)
        build_woodstock_sections(tmp_path / "m", areas=areas)
        model = prepare_optimization(bootstrap_model(tmp_path / "m", horizon=5), horizon=5)
        return list(sequential_replan(model, workdir=tmp_path / "r")["harvest_volume_mcf"])

    first, second = run(), run()
    assert first == second


def test_objective_gap_separates_inconsistency_from_alternate_optima(tmp_path) -> None:
    """The objective-gap diagnostic: NDY's announced tail becomes infeasible/
    suboptimal from the realized state, while the no-flow control's tail stays
    optimal---so the divergence is genuine inconsistency, not alternate optima."""
    from fresh_daugherty.instance.landbases import landbase_areas
    from fresh_daugherty.instance.thesis import HARVEST_FLOW_POLICIES
    from fresh_daugherty.lp import flow_kwargs_for_policy
    from fresh_daugherty.model import (
        bootstrap_model,
        build_woodstock_sections,
        prepare_optimization,
    )
    from fresh_daugherty.replan import consistency_gap_replan

    pol = {p.code: p for p in HARVEST_FLOW_POLICIES}
    results = {}
    for code in ("NDY", "NHF"):
        areas = landbase_areas(1)
        build_woodstock_sections(tmp_path / code / "model", areas=areas)
        model = prepare_optimization(
            bootstrap_model(tmp_path / code / "model", horizon=8), horizon=8
        )
        kw = flow_kwargs_for_policy(pol[code])
        df = consistency_gap_replan(
            model,
            workdir=tmp_path / code / "replan",
            discount_rate=0.04,
            flow_geometry=kw.get("flow_geometry", "none"),
            flow_decrease=kw.get("flow_decrease"),
            flow_increase=kw.get("flow_increase"),
        )
        results[code] = df
    # NHF control: every period's announced decision remains optimal (consistent).
    assert (results["NHF"]["tail_status"] == "optimal").all()
    # NDY: the first period is consistent, and the announced tail becomes
    # non-followable. (Until P16.8, #99, two-storied CH-CW stands carried the
    # sawtimber volume and every NDY replan from period 2 was non-optimal; with
    # the corrected volume the plan is followed for two replans first.)
    ndy = results["NDY"]["tail_status"]
    assert ndy.iloc[0] == "optimal"
    assert (ndy.iloc[1:] != "optimal").any()


def test_gap_replan_honours_carried_flow_history(tmp_path) -> None:
    """P15.1 (issue #83) regression: ``consistency_gap_replan`` must apply
    ``carry_flow_history`` (it was accepted but ignored, silently running the
    reset institution). Under carried NDY the realized path is non-declining
    except where the anchor had to be relaxed, and the gap runner realizes the
    same path as ``sequential_replan`` under the same institution."""
    import numpy as np

    from fresh_daugherty.instance.landbases import landbase_areas
    from fresh_daugherty.model import (
        bootstrap_model,
        build_woodstock_sections,
        prepare_optimization,
    )
    from fresh_daugherty.replan import consistency_gap_replan, sequential_replan

    horizon = 6
    flow = {"flow_geometry": "consecutive", "flow_decrease": 0.0}

    def fresh(name):
        build_woodstock_sections(tmp_path / name, areas=landbase_areas(1))
        model = bootstrap_model(tmp_path / name, horizon=horizon)
        return prepare_optimization(model, horizon=horizon)

    kw = {"discount_rate": 0.04, "rolling_horizon": False, "carry_flow_history": True, **flow}
    gap = consistency_gap_replan(fresh("g"), workdir=tmp_path / "gw", **kw)
    seq = sequential_replan(fresh("s"), workdir=tmp_path / "sw", record_solver_notes=True, **kw)
    realized = gap["realized"].to_numpy()
    notes = list(gap["solver_note"])
    for t in range(1, len(realized)):
        if notes[t] == "relaxed_anchor":
            continue
        rtol = float(notes[t].split("=")[1]) if notes[t].startswith("history_rtol=") else 1e-6
        assert realized[t] >= realized[t - 1] * (1 - rtol) * (1 - 1e-9), (t, notes[t])
    assert np.allclose(realized, seq["harvest_volume_mcf"].to_numpy(), rtol=1e-9)


@pytest.mark.parametrize(
    ("landbase", "policy", "rate"),
    [
        (1, "NDY", 0.04),
        (1, "-10%", 0.04),
        (1, "+/-10%", 0.04),
        (3, "NDY", 0.04),
        (6, "-10%", 0.04),  # P16.2 (#93) S03 reproduction: relaxed at t=12 before
        (8, "NDY", 0.02),
        (9, "+/-20%", 0.0),
    ],
)
def test_null_replanning_reproduces_the_plan(tmp_path, landbase, policy, rate) -> None:
    """Null test (P15.1 #83; widened in P16.2 #93): with a fixed terminal date
    (shrinking horizon) and the flow history carried, each replan solves the
    tail of the original problem from the plan's own state, so the realized
    path must reproduce the open-loop plan, with no material relaxation of the
    carried anchor (Bellman's principle). Before P16.2, float-level drift
    (~1e-6) made the anchor infeasible at capacity-binding periods and it was
    dropped (42 such replans in the P15 institution grid)."""
    import numpy as np

    from fresh_daugherty.instance.thesis import HARVEST_FLOW_POLICIES
    from fresh_daugherty.lp import flow_kwargs_for_policy
    from fresh_daugherty.replan import is_material_relaxation, open_loop_projection

    horizon = 15
    pol = {p.code: p for p in HARVEST_FLOW_POLICIES}[policy]
    flow = flow_kwargs_for_policy(pol)

    def fresh(name):
        build_woodstock_sections(tmp_path / name, areas=landbase_areas(landbase))
        model = bootstrap_model(tmp_path / name, horizon=horizon)
        return prepare_optimization(model, horizon=horizon)

    plan = np.array(open_loop_projection(fresh("p"), discount_rate=rate, **flow))
    seq = sequential_replan(
        fresh("s"),
        workdir=tmp_path / "sw",
        discount_rate=rate,
        rolling_horizon=False,
        carry_flow_history=True,
        record_solver_notes=True,
        **flow,
    )
    notes = list(seq["solver_note"])
    assert not any(is_material_relaxation(n) for n in notes), notes
    # lp.HISTORY_RTOL (1e-6) per period, plus at most a numerical loosening,
    # compounds to well under 1e-3 over 15 periods (5% occurrence tolerance).
    assert np.allclose(seq["harvest_volume_mcf"].to_numpy(), plan, rtol=1e-3, atol=1e-3), np.max(
        np.abs(seq["harvest_volume_mcf"].to_numpy() - plan) / np.maximum(plan, 1.0)
    )


def test_gap_diagnostic_under_carried_bounded_deviation(tmp_path) -> None:
    """P16.1 (#92, S01) end to end: under carried history with a symmetric
    bound, the tail-fixed problem is a genuine restriction of the free one, so
    no objective gap is negative and the diagnostic is not trivially
    'optimal' (before the fix the period-1 band was overwritten by the anchor
    and fixed == free in every replan)."""
    import numpy as np

    from fresh_daugherty.replan import consistency_gap_replan

    build_woodstock_sections(tmp_path / "m", areas=landbase_areas(1))
    model = prepare_optimization(bootstrap_model(tmp_path / "m", horizon=6), horizon=6)
    gap = consistency_gap_replan(
        model,
        workdir=tmp_path / "w",
        discount_rate=0.04,
        flow_geometry="consecutive",
        flow_decrease=0.1,
        flow_increase=0.1,
        rolling_horizon=True,
        carry_flow_history=True,
    )
    tail = gap[gap["period"] > 1]
    g = tail["objective_gap"].dropna().to_numpy()
    free = tail.loc[tail["objective_gap"].notna(), "obj_free"].abs().to_numpy()
    assert (g >= -1e-6 * np.maximum(free, 1.0)).all()
    assert set(tail["tail_status"]) <= {"optimal", "suboptimal", "infeasible"}


def test_dropped_flow_fallback_keeps_cell_settings(monkeypatch) -> None:
    """P16.3 (#94, S15): when every flow variant is infeasible, the last-resort
    solve drops the flow rows but must keep the cell's other settings (it used
    to drop ``discount_path`` and ``flow_denominator`` silently, the defect
    class of #76/#78/#83)."""
    import types

    from fresh_daugherty import replan
    from fresh_daugherty.instance.discount import DISCOUNT_PATHS

    calls: list[dict] = []

    def fake_problem(model, **kw):
        calls.append(kw)
        ok = kw.get("flow_geometry") == "none"
        return types.SimpleNamespace(
            solve=lambda verbose=False: None, status=lambda: "optimal" if ok else "infeasible"
        )

    model = types.SimpleNamespace(
        periods=(1, 2),
        compile_schedule=lambda problem: [],
        reset=lambda: None,
        apply_schedule=lambda *a, **k: None,
        compile_product=lambda p, expr, acode=None: 0.0,
    )
    monkeypatch.setattr(replan, "add_open_loop_problem", fake_problem)
    path = DISCOUNT_PATHS[0]
    notes: list[str] = []
    replan._solve_and_apply(
        model,
        max_period=1,
        discount_rate=0.04,
        discount_path=path,
        flow_denominator="revenue",
        realized_history=(100.0, 100.0),
        flow_tolerance=0.05,
        target_flow_mcf=None,
        flow_geometry="rolling_mean",
        flow_decrease=0.0,
        flow_increase=None,
        abs_period=3,
        notes=notes,
    )
    assert notes == ["dropped_flow"]
    last = calls[-1]
    assert last["flow_geometry"] == "none"
    assert last["discount_path"] is path
    assert last["flow_denominator"] == "revenue"
    assert last["abs_period"] == 3
    # The numerical steps and the full loosening were tried before the history
    # bound and then the flow rows were dropped.
    tried = [c.get("history_rtol") for c in calls]
    assert tried[1:4] == [*replan.NUMERIC_STEPS, 1.0]


def test_minimal_history_relaxation_finds_the_smallest_loosening() -> None:
    """P16.2 (#93): beyond the numerical steps, the loosening is bisected to
    ``HISTORY_RTOL_PRECISION`` (a first version jumped to fixed 1%/10% steps)."""
    import types

    from fresh_daugherty import replan

    needed = 0.0234  # feasible iff the bound is loosened by >= 2.34%

    def solve(rtol):
        return types.SimpleNamespace(status=lambda: "optimal" if rtol >= needed else "infeasible")

    problem, rtol = replan.minimal_history_relaxation(solve)
    assert problem is not None
    assert needed <= rtol <= needed + replan.HISTORY_RTOL_PRECISION
    assert replan.is_material_relaxation(replan.history_note(rtol))
    assert not replan.is_material_relaxation(replan.history_note(1e-5))
    none, r = replan.minimal_history_relaxation(
        lambda _r: types.SimpleNamespace(status=lambda: "infeasible")
    )
    assert none is None and r is None


def test_thesis_window_metrics() -> None:
    """P17.4 (#105): the periods 2-11 window metrics (thesis p. 83) ignore
    period 1 and periods 12-15, and eq. 5-1 divides by announced volume over
    the window only."""
    proj = [100.0] * 15
    real = [100.0] + [90.0] * 10 + [10.0] * 4  # 10% short on 2-11, 90% on 12-15
    m = inconsistency_metrics(proj, real)
    assert m["mean_abs_rel_deviation_2_11"] == pytest.approx(0.10)
    assert m["thesis_volume_inconsistency_2_11"] == pytest.approx(0.10)
    assert m["occurrence_2_11"] is True
    assert m["mean_abs_rel_deviation"] == pytest.approx((10 * 0.1 + 4 * 0.9) / 15)
    short = inconsistency_metrics([100.0] * 5, [100.0] * 4 + [80.0])
    assert short["mean_abs_rel_deviation_2_11"] == pytest.approx(0.05)


@pytest.mark.parametrize("institution", [(True, False), (False, True)])
def test_terminal_rotation_reaches_every_targets_call(tmp_path, monkeypatch, institution) -> None:
    """P19.1 (#118), guard against the recurring defect class (an option
    silently dropped on some call path): every terminal-target computation of
    the announced plan, the free and the tail-fixed replans uses the requested
    rotations."""
    import fresh_daugherty.lp as lp
    from fresh_daugherty.replan import consistency_gap_replan

    seen: list[str] = []
    real = lp.regulated_forest_targets

    def spy(model, *, terminal_rotation="table53"):
        seen.append(terminal_rotation)
        return real(model, terminal_rotation=terminal_rotation)

    monkeypatch.setattr(lp, "regulated_forest_targets", spy)
    rolling, carried = institution
    build_woodstock_sections(tmp_path / "m", areas=landbase_areas(1))
    model = prepare_optimization(bootstrap_model(tmp_path / "m", horizon=4), horizon=4)
    consistency_gap_replan(
        model,
        workdir=tmp_path,
        discount_rate=0.04,
        flow_geometry="consecutive",
        flow_decrease=0.0,
        rolling_horizon=rolling,
        carry_flow_history=carried,
        terminal_rotation="model",
    )
    assert len(seen) >= 1 + 2 * 4 and set(seen) == {"model"}
