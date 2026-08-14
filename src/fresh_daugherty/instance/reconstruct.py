"""Reconstruction of the Daugherty (1991) case-study yield/economics model.

The thesis (ch. 5) gives the case-study *structure* and the anchor tables
(Table 5.2 rotation ranges, Table 5.3 max-PNV/rotation, Table 5.4 mature-type
PNVs) but NOT the raw per-age yield curves or detailed price/cost tables —
those are in the archival USDA 1987 Umpqua Forest Plan Draft EIS. This module
reconstructs the yield and economics model under documented assumptions and
calibrates it to the Table 5.3 / 5.4 anchors.

This is a *reconstruction*, not a transcription. Every assumption is recorded
in ``RECONSTRUCTION_ASSUMPTIONS`` and the achieved fit is reported by
:func:`calibration_report` (and gated in the tests). The anchors are compared
against, not force-fit silently.

Model (documented assumptions):

- Yield: a Chapman-Richards curve per ecoclass, ``V(age) = Vmax * (1 -
  exp(-k*age))**m`` (S-shaped, so mean annual increment culminates and a
  Faustmann optimum exists). The curve is shared per ecoclass (site
  productivity); prescriptions differ by treatment yield-effects and costs.
- Treatments (prescriptions 1-7) apply documented relative yield increments
  and per-acre costs at their thesis timing (vegetation management +
  precommercial thinning one period after planting; fertilization in the
  fourth period; commercial thinning mid-rotation with its own revenue).
- Economics: a net delivered log price per MCF per ecoclass and a per-MCF
  harvest cost; the Faustmann land expectation value (perpetual rotation
  series) at the thesis discount rate (4%), exclusive of planting
  (reforestation) cost per the Table 5.3 note.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from fresh_daugherty.instance.thesis import (
    PNV_ROTATION_ANCHORS,
    PRICE_ESCALATION_RATE,
    PRICE_ESCALATION_YEARS,
    ROTATION_RANGES,
    THESIS_DISCOUNT_RATE,
)

#: Documented reconstruction assumptions (recorded, not silently baked in).
RECONSTRUCTION_ASSUMPTIONS: tuple[str, ...] = (
    "Yield is a Chapman-Richards curve per ecoclass (site productivity); "
    "prescriptions differ by treatment yield-effects and costs, not by the "
    "base curve.",
    "The Faustmann land expectation value (perpetual rotation series) at the "
    "thesis 4% discount rate is the PNV measure, exclusive of planting cost "
    "(per the Table 5.3 note).",
    "Net delivered log price and per-MCF harvest cost are constant per "
    "ecoclass (the thesis varies price by ecoclass and size class; size class "
    "is collapsed here).",
    "Treatment costs/yield-effects are documented reconstruction values "
    "chosen so the calibrated max-LEV and optimal rotation match Table 5.3.",
    "Per-stratum initial areas are not in the thesis; the landbase "
    "definitions (Table 5.5) are reconstructed in "
    "`fresh_daugherty.instance.landbases`.",
)


class YieldParams(BaseModel):
    """Chapman-Richards yield-curve parameters for one ecoclass."""

    vmax: float = Field(gt=0, description="Asymptotic volume (MCF/ac).")
    k: float = Field(gt=0, description="Growth rate (1/yr).")
    m: float = Field(gt=1, description="Shape parameter (>1 gives an S-curve).")


class EconomicsParams(BaseModel):
    """Per-ecoclass economics for the reconstruction."""

    net_price_per_mcf: float = Field(description="Net delivered log price ($/MCF).")
    harvest_cost_per_mcf: float = Field(
        ge=0, description="Harvest cost ($/MCF; sale prep, slash, logging)."
    )


def yield_volume(age_yr: float, params: YieldParams) -> float:
    """Standing volume (MCF/ac) at ``age_yr`` under a Chapman-Richards curve."""
    if age_yr <= 0:
        return 0.0
    return params.vmax * (1.0 - np.exp(-params.k * age_yr)) ** params.m


def escalated_price(base_price: float, year: float) -> float:
    """Delivered log price in ``year``: +1%/yr for the first 50 years, then
    flat (thesis p.74)."""
    return base_price * (1.0 + PRICE_ESCALATION_RATE) ** min(year, PRICE_ESCALATION_YEARS)


def faustmann_lev(
    rotation_yr: float,
    *,
    yield_params: YieldParams,
    econ: EconomicsParams,
    discount_rate: float = THESIS_DISCOUNT_RATE,
    intermediate_cash_flows: tuple[tuple[float, float], ...] = (),
    include_planting: bool = False,
    planting_cost: float = 0.0,
    perpetual: bool = True,
    price_escalation: bool = True,
) -> float:
    """Present net value ($/ac) of a prescription at ``rotation_yr``.

    Net harvest revenue at ``rotation_yr`` plus discounted intermediate cash
    flows (treatment costs/revenues), at the thesis 4% discount rate, with
    delivered log prices escalating 1%/yr for the first 50 years. With
    ``perpetual=True`` (default) this is the Faustmann land expectation value
    (perpetual rotation series); with ``perpetual=False`` it is the
    single-rotation present net value. Planting (reforestation) cost is
    excluded by default (the Table 5.3 anchors are exclusive of it).

    The exact PNV convention in the thesis is ambiguous from the scan
    ("existing stratum established one decade prior", "exclusive of
    reforestation cost"); ``perpetual`` selects between the two readings and
    is a documented reconstruction assumption (see
    ``RECONSTRUCTION_ASSUMPTIONS``).
    """
    if rotation_yr <= 0:
        return -np.inf
    r = discount_rate
    vol = yield_volume(rotation_yr, yield_params)
    price = (
        escalated_price(econ.net_price_per_mcf, rotation_yr)
        if price_escalation
        else econ.net_price_per_mcf
    )
    net_harvest = (price - econ.harvest_cost_per_mcf) * vol
    npv = net_harvest * np.exp(-r * rotation_yr)
    for t, cf in intermediate_cash_flows:
        npv += cf * np.exp(-r * t)
    if include_planting:
        npv -= planting_cost
    if perpetual:
        npv = npv / (1.0 - np.exp(-r * rotation_yr))
    return float(npv)


def best_rotation(
    yield_params: YieldParams,
    econ: EconomicsParams,
    rotation_range: tuple[int, int],
    *,
    discount_rate: float = THESIS_DISCOUNT_RATE,
    intermediate_cash_flows: tuple[tuple[float, float], ...] = (),
) -> tuple[float, float]:
    """Return (optimal rotation yr, max LEV) over the allowed range."""
    lo, hi = rotation_range
    best_r, best_lev = lo, -np.inf
    for r in range(int(lo), int(hi) + 1):
        lev = faustmann_lev(
            float(r),
            yield_params=yield_params,
            econ=econ,
            discount_rate=discount_rate,
            intermediate_cash_flows=intermediate_cash_flows,
        )
        if lev > best_lev:
            best_r, best_lev = r, lev
    return float(best_r), float(best_lev)


def calibration_report() -> pd.DataFrame:
    """Compute the calibrated model's max-LEV/optimal-rotation vs Table 5.3.

    Returns a frame with one row per (ecoclass, prescription) anchor cell and
    the model vs anchor max-PNV and optimal rotation.
    """
    params = calibrated_params()
    rows = []
    for (eco, rx), anchor in PNV_ROTATION_ANCHORS.items():
        if anchor is None:
            continue
        rng = ROTATION_RANGES[(eco, rx)]
        assert rng is not None
        model = params[(eco, rx)]
        opt_r, max_lev = best_rotation(
            model["yield"],
            model["econ"],
            (rng.lo, rng.hi),
            intermediate_cash_flows=model["intermediate"],
        )
        rows.append(
            {
                "ecoclass": eco.value,
                "prescription": int(rx),
                "anchor_pnv": anchor.max_pnv_per_ac,
                "model_pnv": round(max_lev, 1),
                "anchor_rotation": anchor.optimal_rotation_yr,
                "model_rotation": int(opt_r),
            }
        )
    return pd.DataFrame(rows)


# Placeholder for the calibrated parameter set (populated by the calibration
# step). Keyed by (ecoclass, prescription); each value carries the yield
# curve, economics, and intermediate (treatment) cash flows for that cell.
_CALIBRATED: dict | None = None


def calibrated_params() -> dict:
    """Return the calibrated per-cell reconstruction parameters."""
    if _CALIBRATED is None:
        raise RuntimeError(
            "reconstruction parameters not calibrated yet; run the "
            "calibration (fresh_daugherty.instance.reconstruct.calibrate)"
        )
    return _CALIBRATED


__all__ = [
    "RECONSTRUCTION_ASSUMPTIONS",
    "EconomicsParams",
    "YieldParams",
    "best_rotation",
    "calibrated_params",
    "calibration_report",
    "escalated_price",
    "faustmann_lev",
    "yield_volume",
]
