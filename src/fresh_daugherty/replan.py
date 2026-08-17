"""Sequential-replanning simulator and inconsistency measurement (Phase 3).

Reproduces Daugherty (1991)'s iterative LP simulation of sequential
replanning. The open-loop LP is solved; then, repeatedly, the current
period's decision is taken, the forest state is advanced, and the LP is
re-solved from the realized state over the remaining horizon (the future
planner re-optimizing under the same goals). The open-loop plan's projected
trajectory is compared with the realized replanned trajectory; their
divergence is the dynamic inconsistency.

The open-loop LP is an *open-loop* formulation: it precommits future planners
to a schedule. The realized trajectory is what actually unfolds when each
future planner re-optimizes. Their divergence — the plan "not being followed"
— is the failure of Bellman's principle of optimality.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import ws3.forest

from fresh_daugherty.instance.thesis import THESIS_DISCOUNT_RATE
from fresh_daugherty.lp import add_open_loop_problem
from fresh_daugherty.model import (
    bootstrap_model,
    build_woodstock_sections,
    prepare_optimization,
)

_AREA_COLS = ("forest", "ecoclass", "rx", "origin", "state", "age", "area_ac")

#: Occurrence threshold for dynamic inconsistency: a plan is judged dynamically
#: inconsistent when the mean per-period relative divergence between the
#: open-loop projection and the realized replanned trajectory exceeds this
#: tolerance. The default (5%) is far above LP-solver numerical noise (~1e-6)
#: and far below the magnitudes observed on this case study, so the occurrence
#: classification is robust to the exact choice; it is stated explicitly here
#: (and in the paper) so the "occurs in N% of cells" claim is well-defined.
OCCURRENCE_TOLERANCE = 0.05


def extract_areas(model: ws3.forest.ForestModel, period: int) -> pd.DataFrame:
    """Extract the realized area per (development type, age) at ``period``.

    ws3 lowercases theme values; the case-study themes are already
    lowercase-safe (forest/ecoclass/rx codes), so the dtk maps directly back
    to the area-record columns.
    """
    from fresh_daugherty.model import OVER_MATURE_AGE_CAP

    rows = []
    for dtk in model.dtypes:
        dist = model.age_class_distribution(period, mask=dtk)
        for age, area in dist.items():
            if area > 1e-6:
                rows.append(
                    {
                        "forest": dtk[0],
                        "ecoclass": dtk[1],
                        "rx": dtk[2],
                        "origin": dtk[3],
                        "state": dtk[4],
                        # Cap over-mature ages at the plateau: volume has
                        # culminated (flat) past this age, so this is
                        # economically neutral and keeps never-harvested
                        # over-mature stands within the model's age grid.
                        "age": min(int(age), OVER_MATURE_AGE_CAP),
                        "area_ac": float(area),
                    }
                )
    return pd.DataFrame(rows, columns=list(_AREA_COLS))


def build_model(areas: pd.DataFrame, horizon: int, workdir: str | Path) -> ws3.forest.ForestModel:
    """Build a fresh ws3 model from an area distribution over ``horizon``."""
    build_woodstock_sections(workdir, areas=areas)
    model = bootstrap_model(workdir, horizon=horizon)
    return prepare_optimization(model, horizon=horizon)


def _solve_and_apply(
    model,
    *,
    max_period: int | None,
    discount_rate: float,
    flow_tolerance: float,
    target_flow_mcf: float | None,
    flow_geometry: str,
    flow_decrease: float | None,
    flow_increase: float | None,
    abs_period: int = 1,
    prev_harvest_mcf: float | None = None,
) -> list[float]:
    """Solve the open-loop LP, apply its schedule (up to ``max_period``), and
    return the realized per-period harvest volume. ``abs_period`` is the
    absolute calendar period of this subproblem's present (for the price
    clock)."""
    def _build_solve(prev_harvest):
        problem = add_open_loop_problem(
            model,
            flow_coefficient=flow_tolerance,
            discount_rate=discount_rate,
            target_flow_mcf=target_flow_mcf,
            flow_geometry=flow_geometry,
            flow_decrease=flow_decrease,
            flow_increase=flow_increase,
            abs_period=abs_period,
            prev_harvest_mcf=prev_harvest,
            name="open",
        )
        problem.solve(verbose=False)
        return problem

    problem = _build_solve(prev_harvest_mcf)
    if problem.status() != "optimal" and prev_harvest_mcf is not None:
        # The carried sequential-flow policy is infeasible from the realized
        # state (the prior harvest level can't be sustained): the policy must
        # relax --- this is the "declining non-declining yield" made concrete.
        # Retry without the first-period anchor.
        problem = _build_solve(None)
    if problem.status() != "optimal":
        # Last resort: drop the flow constraint entirely rather than crash.
        problem = add_open_loop_problem(
            model,
            flow_coefficient=flow_tolerance,
            discount_rate=discount_rate,
            flow_geometry="none",
            abs_period=abs_period,
            name="open",
        )
        problem.solve(verbose=False)
    schedule = model.compile_schedule(problem)
    model.reset()
    model.apply_schedule(
        schedule,
        max_period=max_period,
        force_integral_area=False,
        override_operability=False,
        fuzzy_age=False,
        recourse_enabled=False,
        verbose=False,
    )
    return [model.compile_product(p, "totvol", acode="harvest") for p in model.periods]


def _solve_subproblem(
    model,
    *,
    discount_rate: float,
    flow_tolerance: float,
    target_flow_mcf: float | None,
    flow_geometry: str,
    flow_decrease: float | None,
    flow_increase: float | None,
    abs_period: int,
    fix_period1_harvest_mcf: float | None = None,
    name: str,
) -> tuple[object, float]:
    """Build and solve the open-loop subproblem on ``model``; return (problem, objective)."""
    problem = add_open_loop_problem(
        model,
        flow_coefficient=flow_tolerance,
        discount_rate=discount_rate,
        target_flow_mcf=target_flow_mcf,
        flow_geometry=flow_geometry,
        flow_decrease=flow_decrease,
        flow_increase=flow_increase,
        abs_period=abs_period,
        fix_period1_harvest_mcf=fix_period1_harvest_mcf,
        name=name,
    )
    problem.solve(verbose=False)
    obj = problem.z() if problem.status() == "optimal" else float("nan")
    return problem, obj


def consistency_gap_replan(
    model: ws3.forest.ForestModel,
    *,
    workdir: str | Path,
    discount_rate: float = THESIS_DISCOUNT_RATE,
    flow_tolerance: float = 0.05,
    target_flow_mcf: float | None = None,
    flow_geometry: str = "period1",
    flow_decrease: float | None = None,
    flow_increase: float | None = None,
    carry_flow_history: bool = True,
    rolling_horizon: bool = True,
) -> pd.DataFrame:
    """Sequential replanning with an objective-gap consistency diagnostic.

    At each replan period the announced (period-0 open-loop) plan's harvest for
    that period is evaluated against the re-solved subproblem: we solve the
    subproblem freely (``obj_free``) and with the period-1 harvest fixed to the
    announced value (``obj_fixed``). The ``objective_gap = obj_free -
    obj_fixed`` measures how much the re-solver strictly improves on the
    announced decision. A positive gap means the announced plan's tail is
    *strictly suboptimal*---genuine dynamic inconsistency, distinguishable from
    merely choosing an alternate LP optimum (which would give gap ~ 0).

    Returns a per-period frame: period, announced, realized, obj_free,
    obj_fixed, objective_gap.
    """
    workdir = Path(workdir)
    horizon = model.horizon
    announced = open_loop_projection(
        model,
        discount_rate=discount_rate,
        flow_tolerance=flow_tolerance,
        target_flow_mcf=target_flow_mcf,
        flow_geometry=flow_geometry,
        flow_decrease=flow_decrease,
        flow_increase=flow_increase,
    )
    rows = []
    current = model
    realized: list[float] = []
    for t in range(1, horizon + 1):
        kw = {
            "discount_rate": discount_rate,
            "flow_tolerance": flow_tolerance,
            "target_flow_mcf": target_flow_mcf,
            "flow_geometry": flow_geometry,
            "flow_decrease": flow_decrease,
            "flow_increase": flow_increase,
            "abs_period": t,
        }
        # Free subproblem (the re-solver's choice).
        prob_free, obj_free = _solve_subproblem(current, name="free", **kw)
        # Tail-fixed subproblem (the announced plan's period-t decision).
        _, obj_fixed = _solve_subproblem(
            current, name="fixed", fix_period1_harvest_mcf=announced[t - 1], **kw
        )
        # Realized decision = the free subproblem's period-1 harvest; apply it.
        schedule = current.compile_schedule(prob_free)
        current.reset()
        current.apply_schedule(
            schedule,
            max_period=1,
            force_integral_area=False,
            override_operability=False,
            fuzzy_age=False,
            recourse_enabled=False,
            verbose=False,
        )
        r_t = current.compile_product(1, "totvol", acode="harvest")
        realized.append(r_t)
        # Tail status: is the announced plan's period-t decision still optimal
        # from the realized state? "optimal" (free==fixed), "suboptimal"
        # (feasible but strictly worse), or "infeasible" (cannot be implemented).
        gap = (
            float(obj_free - obj_fixed)
            if obj_free == obj_free and obj_fixed == obj_fixed
            else float("nan")
        )
        if obj_fixed != obj_fixed:  # NaN -> infeasible
            status = "infeasible"
        elif gap > 1e-6 * max(abs(obj_free), 1.0):
            status = "suboptimal"
        else:
            status = "optimal"
        rows.append(
            {
                "period": t,
                "announced": float(announced[t - 1]),
                "realized": float(r_t),
                "obj_free": float(obj_free),
                "obj_fixed": float(obj_fixed),
                "objective_gap": gap,
                "tail_status": status,
            }
        )
        if t == horizon:
            break
        state = extract_areas(current, 2)
        next_horizon = horizon if rolling_horizon else current.horizon - 1
        current = build_model(state, next_horizon, workdir / f"replan_{t}")
    return pd.DataFrame(rows)


def open_loop_projection(
    model: ws3.forest.ForestModel,
    *,
    discount_rate: float = THESIS_DISCOUNT_RATE,
    flow_tolerance: float = 0.05,
    target_flow_mcf: float | None = None,
    flow_geometry: str = "period1",
    flow_decrease: float | None = None,
    flow_increase: float | None = None,
    abs_period: int = 1,
) -> list[float]:
    """The open-loop plan's projected per-period harvest volume (full horizon)."""
    return _solve_and_apply(
        model,
        max_period=None,
        discount_rate=discount_rate,
        flow_tolerance=flow_tolerance,
        target_flow_mcf=target_flow_mcf,
        flow_geometry=flow_geometry,
        flow_decrease=flow_decrease,
        flow_increase=flow_increase,
        abs_period=abs_period,
    )


def sequential_replan(
    model: ws3.forest.ForestModel,
    *,
    workdir: str | Path,
    discount_rate: float = THESIS_DISCOUNT_RATE,
    flow_tolerance: float = 0.05,
    target_flow_mcf: float | None = None,
    flow_geometry: str = "period1",
    flow_decrease: float | None = None,
    flow_increase: float | None = None,
    carry_flow_history: bool = True,
    rolling_horizon: bool = True,
) -> pd.DataFrame:
    """Run the sequential-replanning simulation.

    At each period, re-solve the open-loop LP from the realized state, take
    the current period's decision, apply it, and advance. With
    ``rolling_horizon=True`` (default) each replan solves a full-length
    problem from the realized state (the horizon rolls forward with the
    present), avoiding the terminal-period artifact of a shrinking horizon;
    with ``rolling_horizon=False`` the replan is over the shrinking remaining
    horizon. Returns a frame of the realized per-period harvest volume.
    """
    workdir = Path(workdir)
    horizon = model.horizon
    realized: list[float] = []
    current = model
    prev_harvest: float | None = None
    for t in range(1, horizon + 1):
        # Re-solve the open-loop LP from the current state, take the current
        # period's decision (apply only period 1 of this sub-horizon). Anchor the
        # subproblem's first-period flow to the realized previous harvest so the
        # replanned policy is the SAME sequential-flow policy (not a reset one).
        volumes = _solve_and_apply(
            current,
            max_period=1,
            discount_rate=discount_rate,
            flow_tolerance=flow_tolerance,
            target_flow_mcf=target_flow_mcf,
            flow_geometry=flow_geometry,
            flow_decrease=flow_decrease,
            flow_increase=flow_increase,
            abs_period=t,
            prev_harvest_mcf=prev_harvest if carry_flow_history else None,
        )
        realized.append(volumes[0])
        prev_harvest = volumes[0]
        if t == horizon:
            break
        # Extract the realized state at the start of the next period and build
        # a fresh model for the next replan. After applying period 1 the model
        # has advanced one period, so the "now" state for the next replan is the
        # period-2 age distribution (extracting at period 1 would re-read the
        # just-planted age-0 state and regenerated stands would never age).
        state = extract_areas(current, 2)
        next_horizon = horizon if rolling_horizon else current.horizon - 1
        current = build_model(state, next_horizon, workdir / f"replan_{t}")
    return pd.DataFrame({"period": list(range(1, horizon + 1)), "harvest_volume_mcf": realized})


def inconsistency_metrics(
    projected: list[float],
    realized: list[float],
    *,
    occurrence_tolerance: float = OCCURRENCE_TOLERANCE,
) -> dict[str, float]:
    """Dynamic-inconsistency metrics from the projected vs realized volumes.

    The open-loop plan's projected per-period harvest volume vs the realized
    replanned trajectory. Formally, with projection ``p = (p_1, ..., p_T)`` and
    realized trajectory ``r = (r_1, ..., r_T)``, the per-period relative
    deviation is the *symmetric* relative change

        delta_t = |p_t - r_t| / max(|p_t|, |r_t|, eps),

    which is bounded in [0, 1] and robust to near-zero baselines (a projected
    lull that the replanning fills, or vice versa, gives delta_t ~ 1 rather than
    an exploding ratio). ``eps`` is a small floor so a both-zero period scores 0.
    The reported magnitudes are the mean and max of ``delta_t`` over the horizon
    and the relative change in total volume ``(sum r - sum p) / max(|sum p|, 1)``.
    A plan is judged dynamically inconsistent (``occurrence``) when the mean
    relative deviation exceeds ``occurrence_tolerance`` (default
    ``OCCURRENCE_TOLERANCE``). The first-period decision is consistent by
    construction, so the divergence is in the plan's tail, as the theory predicts.
    """
    n = min(len(projected), len(realized))
    p = np.array(projected[:n], dtype=float)
    r = np.array(realized[:n], dtype=float)
    # Symmetric denominator, bounded in [0, 1]; a small floor handles both-zero.
    floor = max(float(np.abs(p).mean()), float(np.abs(r).mean()), 1.0) * 1e-6
    denom = np.maximum(np.maximum(np.abs(p), np.abs(r)), floor)
    rel = np.abs(p - r) / denom
    mean_rel = float(rel.mean())
    return {
        "max_abs_rel_deviation": float(rel.max()),
        "mean_abs_rel_deviation": mean_rel,
        "total_projected": float(p.sum()),
        "total_realized": float(r.sum()),
        "total_rel_change": float((r.sum() - p.sum()) / max(abs(p.sum()), 1.0)),
        "occurrence": bool(mean_rel > occurrence_tolerance),
        "occurrence_tolerance": float(occurrence_tolerance),
    }


__all__ = [
    "OCCURRENCE_TOLERANCE",
    "build_model",
    "extract_areas",
    "inconsistency_metrics",
    "open_loop_projection",
    "sequential_replan",
]
