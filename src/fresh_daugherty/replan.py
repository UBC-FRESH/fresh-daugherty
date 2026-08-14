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

from fresh_daugherty.lp import add_open_loop_problem
from fresh_daugherty.model import (
    bootstrap_model,
    build_woodstock_sections,
    prepare_optimization,
)

_AREA_COLS = ("forest", "ecoclass", "rx", "origin", "state", "age", "area_ac")


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


def _solve_and_apply(model, *, max_period: int | None) -> list[float]:
    """Solve the open-loop LP, apply its schedule (up to ``max_period``), and
    return the realized per-period harvest volume."""
    problem = add_open_loop_problem(model, name="open")
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


def open_loop_projection(model: ws3.forest.ForestModel) -> list[float]:
    """The open-loop plan's projected per-period harvest volume (full horizon)."""
    return _solve_and_apply(model, max_period=None)


def sequential_replan(
    model: ws3.forest.ForestModel,
    *,
    workdir: str | Path,
) -> pd.DataFrame:
    """Run the sequential-replanning simulation.

    At each period, re-solve the open-loop LP from the realized state, take
    the current period's decision, apply it, and advance. Returns a frame of
    the realized per-period harvest volume. The model passed in is used for
    the first (full-horizon) solve and is not modified beyond that.
    """
    workdir = Path(workdir)
    horizon = model.horizon
    realized: list[float] = []
    current = model
    for t in range(1, horizon + 1):
        # Re-solve the open-loop LP from the current state, take the current
        # period's decision (apply only period 1 of this sub-horizon).
        volumes = _solve_and_apply(current, max_period=1)
        realized.append(volumes[0])
        if t == horizon:
            break
        # Extract the realized state at the start of the next period and build
        # a fresh model over the remaining horizon.
        state = extract_areas(current, 1)
        current = build_model(state, current.horizon - 1, workdir / f"replan_{t}")
    return pd.DataFrame({"period": list(range(1, horizon + 1)), "harvest_volume_mcf": realized})


def inconsistency_metrics(projected: list[float], realized: list[float]) -> dict[str, float]:
    """Dynamic-inconsistency metrics from the projected vs realized volumes.

    The open-loop plan's projected per-period harvest volume vs the realized
    replanned trajectory. Metrics: max and mean absolute deviation, and the
    relative change in total volume.
    """
    n = min(len(projected), len(realized))
    p = np.array(projected[:n], dtype=float)
    r = np.array(realized[:n], dtype=float)
    denom = np.maximum(np.abs(p), 1.0)
    rel = np.abs(p - r) / denom
    return {
        "max_abs_rel_deviation": float(rel.max()),
        "mean_abs_rel_deviation": float(rel.mean()),
        "total_projected": float(p.sum()),
        "total_realized": float(r.sum()),
        "total_rel_change": float((r.sum() - p.sum()) / max(abs(p.sum()), 1.0)),
    }


__all__ = [
    "build_model",
    "extract_areas",
    "inconsistency_metrics",
    "open_loop_projection",
    "sequential_replan",
]
