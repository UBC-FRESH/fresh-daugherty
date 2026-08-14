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
) -> ExperimentResult:
    """Run one experiment cell (open-loop projection + sequential replan)."""
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
    )

    # Sequential replanning under the same policy (the "same goals").
    realized_df = sequential_replan(
        model,
        workdir=workdir,
        discount_rate=discount_rate,
        flow_tolerance=flow_tolerance,
        target_flow_mcf=target_flow_mcf,
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
                )
                rows.append(
                    {
                        "landbase": lb,
                        "discount_rate": rate,
                        "flow_tolerance": ft,
                        "horizon": horizon,
                        **result.metrics,
                    }
                )
    return pd.DataFrame(rows)


__all__ = ["ExperimentResult", "run_experiment", "run_experiment_grid"]
