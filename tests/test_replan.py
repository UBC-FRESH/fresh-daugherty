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
    model = prepare_optimization(bootstrap_model(tmp / "model", horizon=6), horizon=6)
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
    # NDY: the first period is consistent, then the announced tail is not followable.
    assert results["NDY"]["tail_status"].iloc[0] == "optimal"
    assert (results["NDY"]["tail_status"].iloc[1:] != "optimal").all()


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
    relaxed = (gap["solver_note"] == "relaxed_anchor").to_numpy()
    for t in range(1, len(realized)):
        if not relaxed[t]:
            assert realized[t] >= realized[t - 1] * (1 - 1e-6), (t, realized[t - 1], realized[t])
    assert np.allclose(realized, seq["harvest_volume_mcf"].to_numpy(), rtol=1e-9)


def test_null_replanning_reproduces_the_plan(tmp_path) -> None:
    """P15.1 (issue #83) null test: with a fixed terminal date (shrinking
    horizon) and the flow history carried, each replan solves the tail of the
    original problem from the plan's own state, so the realized path must
    reproduce the open-loop plan. Before the fix, float noise in realized
    harvests (~1e-6 above the plan level) made the exact carried NDY anchor
    infeasible, the anchor was dropped, and the path diverged (landbase 1,
    NDY, 4%: from period 7, up to 15%)."""
    import numpy as np

    from fresh_daugherty.instance.landbases import landbase_areas
    from fresh_daugherty.model import (
        bootstrap_model,
        build_woodstock_sections,
        prepare_optimization,
    )
    from fresh_daugherty.replan import open_loop_projection, sequential_replan

    horizon = 15
    flow = {"flow_geometry": "consecutive", "flow_decrease": 0.0}

    def fresh(name):
        build_woodstock_sections(tmp_path / name, areas=landbase_areas(1))
        model = bootstrap_model(tmp_path / name, horizon=horizon)
        return prepare_optimization(model, horizon=horizon)

    plan = np.array(open_loop_projection(fresh("p"), discount_rate=0.04, **flow))
    seq = sequential_replan(
        fresh("s"),
        workdir=tmp_path / "sw",
        discount_rate=0.04,
        rolling_horizon=False,
        carry_flow_history=True,
        record_solver_notes=True,
        **flow,
    )
    # Tolerance: lp.HISTORY_RTOL (1e-6) lets each period sit up to 1e-6 below
    # the previous harvest; over 15 periods this compounds to ~2e-5. Still far
    # below the 5% occurrence tolerance, and no anchor may be relaxed.
    assert np.allclose(seq["harvest_volume_mcf"].to_numpy(), plan, rtol=1e-4)
    assert (seq["solver_note"] == "ok").all()


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
