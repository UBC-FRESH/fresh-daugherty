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
                        "age": int(age),
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
) -> list[float]:
    """Solve the open-loop LP, apply its schedule (up to ``max_period``), and
    return the realized per-period harvest volume."""
    problem = add_open_loop_problem(
        model,
        flow_coefficient=flow_tolerance,
        discount_rate=discount_rate,
        target_flow_mcf=target_flow_mcf,
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


def open_loop_projection(
    model: ws3.forest.ForestModel,
    *,
    discount_rate: float = THESIS_DISCOUNT_RATE,
    flow_tolerance: float = 0.05,
    target_flow_mcf: float | None = None,
) -> list[float]:
    """The open-loop plan's projected per-period harvest volume (full horizon)."""
    return _solve_and_apply(
        model,
        max_period=None,
        discount_rate=discount_rate,
        flow_tolerance=flow_tolerance,
        target_flow_mcf=target_flow_mcf,
    )


def sequential_replan(
    model: ws3.forest.ForestModel,
    *,
    workdir: str | Path,
    discount_rate: float = THESIS_DISCOUNT_RATE,
    flow_tolerance: float = 0.05,
    target_flow_mcf: float | None = None,
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
    for t in range(1, horizon + 1):
        # Re-solve the open-loop LP from the current state, take the current
        # period's decision (apply only period 1 of this sub-horizon).
        volumes = _solve_and_apply(
            current,
            max_period=1,
            discount_rate=discount_rate,
            flow_tolerance=flow_tolerance,
            target_flow_mcf=target_flow_mcf,
        )
        realized.append(volumes[0])
        if t == horizon:
            break
        # Extract the realized state at the start of the next period and build
        # a fresh model for the next replan.
        state = extract_areas(current, 1)
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
    deviation is

        delta_t = |p_t - r_t| / max(|p_t|, 1),

    and the reported magnitudes are the mean and max of ``delta_t`` over the
    horizon and the relative change in total volume
    ``(sum r - sum p) / max(|sum p|, 1)``. A plan is judged dynamically
    inconsistent (``occurrence``) when the mean relative deviation exceeds
    ``occurrence_tolerance`` (default ``OCCURRENCE_TOLERANCE``). The
    first-period decision is consistent by construction (the realized period-1
    harvest is the open-loop period-1 decision), so the divergence is in the
    plan's tail, exactly as the theory predicts.
    """
    n = min(len(projected), len(realized))
    p = np.array(projected[:n], dtype=float)
    r = np.array(realized[:n], dtype=float)
    denom = np.maximum(np.abs(p), 1.0)
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
