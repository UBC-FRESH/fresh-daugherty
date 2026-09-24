"""Even-flow pattern metric + max-harvest-cap search (Phase 10 / E2, issues #58-#59).

E2 swaps the NDY flow link for a simple per-period cap ``H_t <= cap`` and
iteratively re-solves, tightening the cap, until the harvest trajectory
qualifies as *even flow*. This module provides:

- :class:`EvenFlowCriteria` — the typed, recorded even-flow thresholds; and
  :func:`assess_even_flow` — the composite pattern metric over a trajectory
  (OLS trend slope, max period-over-period relative fluctuation, coefficient
  of variation), returning an :class:`EvenFlowReport`.
- :func:`calibrate_even_flow_cap` (P10.3) — bisection on the cap to the
  loosest value whose trajectory meets the criteria.

Design decisions (per `planning/v0.2.0-plan.md` §E2): evenness is scored on
the **realized sequential-replanning trajectory** (the primary, honest
criterion) and reported for the open-loop projection as secondary. Threshold
defaults are recorded here and in every cell record so sensitivity can be
reported.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class EvenFlowCriteria:
    """Even-flow acceptance thresholds (recorded per cell).

    - ``max_slope_rel``: |OLS slope of H_t on t| per period, as a fraction of
      the mean harvest (a downward trend counts against evenness, as does an
      upward one). Default 1% of the mean per period.
    - ``max_fluctuation``: max period-over-period relative change
      ``|H_{t+1} - H_t| / H̄``. Default 5% of the mean.
    - ``max_cv``: coefficient of variation (SD/mean) over the horizon.
      Default 5%.
    """

    max_slope_rel: float = 0.01
    max_fluctuation: float = 0.05
    max_cv: float = 0.05


#: Default even-flow criteria (recorded in every cell record).
DEFAULT_CRITERIA = EvenFlowCriteria()


@dataclass(frozen=True)
class EvenFlowReport:
    """The even-flow assessment of one trajectory."""

    mean: float
    slope: float  # OLS slope of H_t on t (MCF per period)
    slope_rel: float  # |slope| / mean
    max_fluctuation: float  # max |ΔH_t| / mean
    cv: float  # SD / mean
    is_even: bool


def assess_even_flow(
    volumes: list[float] | tuple[float, ...],
    criteria: EvenFlowCriteria = DEFAULT_CRITERIA,
) -> EvenFlowReport:
    """Score a harvest trajectory against the even-flow criteria."""
    v = np.asarray(volumes, dtype=float)
    mean = float(v.mean()) if v.size else 0.0
    if v.size < 2 or mean <= 1e-9:
        # A (near-)zero or degenerate trajectory is not a viable even flow.
        return EvenFlowReport(
            mean=mean,
            slope=0.0,
            slope_rel=0.0,
            max_fluctuation=0.0,
            cv=float("inf"),
            is_even=False,
        )
    t = np.arange(1, v.size + 1, dtype=float)
    slope = float(np.polyfit(t, v, 1)[0])
    slope_rel = abs(slope) / mean
    max_fluct = float(np.abs(np.diff(v)).max()) / mean
    cv = float(v.std() / mean)
    is_even = (
        slope_rel <= criteria.max_slope_rel
        and max_fluct <= criteria.max_fluctuation
        and cv <= criteria.max_cv
    )
    return EvenFlowReport(
        mean=mean,
        slope=slope,
        slope_rel=slope_rel,
        max_fluctuation=max_fluct,
        cv=cv,
        is_even=is_even,
    )


@dataclass(frozen=True)
class CapSearchRecord:
    """One cap-search cell: the calibrated cap and its evidence."""

    landbase: int
    discount_rate: float
    horizon: int
    calibrated_cap_mcf: float | None  # None if the search failed to converge
    converged: bool
    iterations: int
    criteria: EvenFlowCriteria
    realized_report: EvenFlowReport
    projected_report: EvenFlowReport
    projected: tuple[float, ...] = field(repr=False, default=())
    realized: tuple[float, ...] = field(repr=False, default=())
    history: tuple[dict, ...] = field(repr=False, default=())


def calibrate_even_flow_cap(
    model,
    *,
    landbase: int,
    workdir: str | Path,
    discount_rate: float,
    criteria: EvenFlowCriteria = DEFAULT_CRITERIA,
    rel_tol: float = 0.005,
    max_iter: int = 25,
) -> CapSearchRecord:
    """Bisect the max-harvest cap to the loosest value giving realized even flow.

    Each iteration runs a full sequential-replanning simulation under the
    trial cap (``target_flow_mcf``) and scores the *realized* trajectory
    against ``criteria``. Monotone tightening keeps bisection valid: a tighter
    cap can only flatten the trajectory. The bracket is ``[0, H_max]`` where
    ``H_max`` is the unconstrained (NHF) maximum projected period harvest; a
    zero-cap floor is never viable (a zero trajectory fails the metric). The
    search stops when the bracket width is within ``rel_tol`` of the cap or
    ``max_iter`` iterations are exhausted. Returns the calibrated record with
    the full iteration history.
    """
    from fresh_daugherty.replan import open_loop_projection, sequential_replan

    workdir = Path(workdir)
    horizon = model.horizon

    def _realized_report(cap: float) -> tuple[EvenFlowReport, EvenFlowReport, list, list]:
        projected = open_loop_projection(model, target_flow_mcf=cap)
        realized_df = sequential_replan(
            model,
            workdir=workdir / f"cap_{cap:.1f}",
            discount_rate=discount_rate,
            target_flow_mcf=cap,
        )
        realized = list(realized_df["harvest_volume_mcf"])
        return (
            assess_even_flow(realized, criteria),
            assess_even_flow(projected, criteria),
            projected,
            realized,
        )

    history: list[dict] = []
    # Bracket: H_max (unconstrained peak; almost surely not even) .. 0 (never
    # viable). If H_max is already even, the cap is unnecessary (record H_max).
    nhf = open_loop_projection(model, flow_geometry="none")
    hi = float(max(nhf))
    rep_r, rep_p, proj, real = _realized_report(hi)
    history.append({"cap": hi, "is_even": rep_r.is_even, "cv": rep_r.cv})
    if rep_r.is_even:
        return CapSearchRecord(
            landbase=landbase,
            discount_rate=discount_rate,
            horizon=horizon,
            calibrated_cap_mcf=hi,
            converged=True,
            iterations=1,
            criteria=criteria,
            realized_report=rep_r,
            projected_report=rep_p,
            projected=tuple(proj),
            realized=tuple(real),
            history=tuple(history),
        )
    lo = 0.0
    best: tuple[float, EvenFlowReport, EvenFlowReport, list, list] | None = None
    it = 1
    while it < max_iter and (hi - lo) > rel_tol * max(hi, 1.0):
        mid = 0.5 * (lo + hi)
        rep_r, rep_p, proj, real = _realized_report(mid)
        history.append({"cap": mid, "is_even": rep_r.is_even, "cv": rep_r.cv})
        it += 1
        if rep_r.is_even:
            best = (mid, rep_r, rep_p, proj, real)
            lo = mid  # can loosen
        else:
            hi = mid  # must tighten
    if best is None:
        return CapSearchRecord(
            landbase=landbase,
            discount_rate=discount_rate,
            horizon=horizon,
            calibrated_cap_mcf=None,
            converged=False,
            iterations=it,
            criteria=criteria,
            realized_report=rep_r,
            projected_report=rep_p,
            projected=tuple(proj),
            realized=tuple(real),
            history=tuple(history),
        )
    cap, rep_r, rep_p, proj, real = best
    return CapSearchRecord(
        landbase=landbase,
        discount_rate=discount_rate,
        horizon=horizon,
        calibrated_cap_mcf=cap,
        converged=True,
        iterations=it,
        criteria=criteria,
        realized_report=rep_r,
        projected_report=rep_p,
        projected=tuple(proj),
        realized=tuple(real),
        history=tuple(history),
    )


__all__ = [
    "DEFAULT_CRITERIA",
    "CapSearchRecord",
    "EvenFlowCriteria",
    "EvenFlowReport",
    "assess_even_flow",
    "calibrate_even_flow_cap",
]
