"""Case-study experiments: inconsistency across conditions (Phase 4).

Sweeps the Daugherty (1991) experimental factors — initial forest condition
(landbase), harvest policy (harvest-flow tolerance), and interest rate — and
measures the occurrence and magnitude of dynamic inconsistency per cell (the
thesis's empirical core: inconsistency occurs over a wide range of initial
forest conditions and harvest policies).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from fresh_daugherty.instance.landbases import landbase_areas
from fresh_daugherty.instance.thesis import HarvestFlowPolicy
from fresh_daugherty.lp import flow_kwargs_for_policy
from fresh_daugherty.model import bootstrap_model, build_woodstock_sections, prepare_optimization
from fresh_daugherty.replan import (
    inconsistency_metrics,
    open_loop_projection,
    sequential_replan,
)


@dataclass(frozen=True)
class ExperimentResult:
    """One experiment cell: open-loop projection vs realized replan."""

    landbase: int
    discount_rate: float
    flow_tolerance: float
    horizon: int
    projected: tuple[float, ...]
    realized: tuple[float, ...]
    metrics: dict[str, float]


def run_experiment(
    *,
    landbase: int,
    discount_rate: float,
    flow_tolerance: float,
    horizon: int,
    workdir: str | Path,
    target_flow_mcf: float | None = None,
    flow_geometry: str = "period1",
    flow_decrease: float | None = None,
    flow_increase: float | None = None,
    flow_policy: HarvestFlowPolicy | None = None,
) -> ExperimentResult:
    """Run one experiment cell (open-loop projection + sequential replan).

    If ``flow_policy`` (a thesis Table 5.6 harvest-flow policy) is given, it
    overrides ``flow_geometry``/``flow_decrease``/``flow_increase`` with the
    policy's consecutive sequential-flow form.
    """
    if flow_policy is not None:
        flow_kwargs = flow_kwargs_for_policy(flow_policy)
        flow_geometry = flow_kwargs.get("flow_geometry", flow_geometry)
        flow_decrease = flow_kwargs.get("flow_decrease")
        flow_increase = flow_kwargs.get("flow_increase")
    workdir = Path(workdir)
    areas = landbase_areas(landbase)
    build_woodstock_sections(workdir / "model", areas=areas)
    model = prepare_optimization(
        bootstrap_model(workdir / "model", horizon=horizon), horizon=horizon
    )

    # Open-loop projection under this cell's discount rate + flow tolerance.
    projected = open_loop_projection(
        model,
        discount_rate=discount_rate,
        flow_tolerance=flow_tolerance,
        target_flow_mcf=target_flow_mcf,
        flow_geometry=flow_geometry,
        flow_decrease=flow_decrease,
        flow_increase=flow_increase,
    )

    # Sequential replanning under the same policy (the "same goals").
    realized_df = sequential_replan(
        model,
        workdir=workdir,
        discount_rate=discount_rate,
        flow_tolerance=flow_tolerance,
        target_flow_mcf=target_flow_mcf,
        flow_geometry=flow_geometry,
        flow_decrease=flow_decrease,
        flow_increase=flow_increase,
    )
    realized = list(realized_df["harvest_volume_mcf"])
    return ExperimentResult(
        landbase=landbase,
        discount_rate=discount_rate,
        flow_tolerance=flow_tolerance,
        horizon=horizon,
        projected=tuple(projected),
        realized=tuple(realized),
        metrics=inconsistency_metrics(projected, realized),
    )


def run_experiment_grid(
    *,
    landbases: tuple[int, ...],
    discount_rates: tuple[float, ...],
    flow_tolerances: tuple[float, ...],
    horizon: int,
    workdir: str | Path,
    target_flow_by_landbase: dict[int, float] | None = None,
    flow_geometry: str = "period1",
    flow_decrease: float | None = None,
    flow_increase: float | None = None,
) -> pd.DataFrame:
    """Run the experiment grid and return the occurrence/magnitude table."""
    workdir = Path(workdir)
    rows = []
    for lb in landbases:
        for rate in discount_rates:
            for ft in flow_tolerances:
                result = run_experiment(
                    landbase=lb,
                    discount_rate=rate,
                    flow_tolerance=ft,
                    horizon=horizon,
                    workdir=workdir / f"lb{lb}_r{rate}_ft{ft}",
                    target_flow_mcf=(target_flow_by_landbase or {}).get(lb),
                    flow_geometry=flow_geometry,
                    flow_decrease=flow_decrease,
                    flow_increase=flow_increase,
                )
                rows.append(
                    {
                        "landbase": lb,
                        "discount_rate": rate,
                        "flow_tolerance": ft,
                        "flow_geometry": flow_geometry,
                        "horizon": horizon,
                        **result.metrics,
                    }
                )
    return pd.DataFrame(rows)


def _policy_slug(code: str) -> str:
    """Filesystem-safe slug for a harvest-flow policy code (e.g. '+/-10%' -> 'pm10pct')."""
    return code.replace("+", "p").replace("/", "").replace("-", "m").replace("%", "pct")


def _run_policy_cell(args: tuple) -> dict:
    """Run one (landbase, rate, policy) grid cell. Module-level so it is
    picklable for the process pool."""
    lb, rate, pol, horizon, cell_workdir = args
    from fresh_daugherty.instance.reconstruct import calibrate

    calibrate()
    result = run_experiment(
        landbase=lb,
        discount_rate=rate,
        flow_tolerance=0.0,  # unused when flow_policy is given
        horizon=horizon,
        workdir=cell_workdir,
        flow_policy=pol,
    )
    return {
        "landbase": lb,
        "discount_rate": rate,
        "flow_policy": pol.code,
        "max_decrease": pol.max_decrease,
        "max_increase": pol.max_increase,
        "horizon": horizon,
        "projected": result.projected,
        "realized": result.realized,
        **result.metrics,
    }


def run_policy_grid(
    *,
    landbases: tuple[int, ...],
    discount_rates: tuple[float, ...],
    policies: tuple[HarvestFlowPolicy, ...],
    horizon: int,
    workdir: str | Path,
    workers: int = 1,
) -> pd.DataFrame:
    """Run the thesis experiment grid: landbase x discount rate x harvest-flow policy.

    Reproduces Daugherty (1991)'s experiment design — the Table 5.6
    harvest-flow policies (NHF, NDY, -10%, -20%, +/-10%, +/-20%) crossed with
    discount rates and landbases. Each cell is a full sequential-replanning
    simulation under the policy's consecutive sequential-flow constraint.
    Cells are independent and run in parallel across ``workers`` processes
    (each cell gets a unique workdir). Returns ``(summary, trajectories)``:
    ``summary`` has one row per cell with the occurrence/magnitude metrics;
    ``trajectories`` is a long-format frame (one row per cell x period) with the
    open-loop projected and realized replanned harvest volumes, so the full
    benchmark record can be published and re-analyzed.
    """
    workdir = Path(workdir)
    cells = [
        (lb, rate, pol, horizon, workdir / f"lb{lb}_r{rate}_{_policy_slug(pol.code)}")
        for lb in landbases
        for rate in discount_rates
        for pol in policies
    ]
    if workers and workers > 1:
        from concurrent.futures import ProcessPoolExecutor

        from fresh_daugherty.instance.reconstruct import calibrate

        calibrate()  # warm the parent so forked workers inherit the calibration
        with ProcessPoolExecutor(max_workers=workers) as ex:
            rows = list(ex.map(_run_policy_cell, cells))
    else:
        rows = [_run_policy_cell(c) for c in cells]

    summary = pd.DataFrame(
        [{k: v for k, v in r.items() if k not in ("projected", "realized")} for r in rows]
    )
    traj_rows = []
    for r in rows:
        for period, (p, rl) in enumerate(zip(r["projected"], r["realized"], strict=True), start=1):
            traj_rows.append(
                {
                    "landbase": r["landbase"],
                    "discount_rate": r["discount_rate"],
                    "flow_policy": r["flow_policy"],
                    "period": period,
                    "projected_mcf": p,
                    "realized_mcf": rl,
                }
            )
    trajectories = pd.DataFrame(traj_rows)
    return summary, trajectories


__all__ = [
    "ExperimentResult",
    "run_experiment",
    "run_experiment_grid",
    "run_policy_grid",
]
