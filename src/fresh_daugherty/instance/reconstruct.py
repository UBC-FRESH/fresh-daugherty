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
    Ecoclass,
    Prescription,
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


# --------------------------------------------------------------------------
# Calibration
# --------------------------------------------------------------------------
#
# The reconstruction is calibrated to the Table 5.3 anchors. The yield-curve
# *shape* is grounded in the real Umpqua LRMP data: the Chapman-Richards
# growth rate ``k`` is set so the curve's MAI culminates at the ecoclass's
# documented 95%-CMAI age (Table IV-3, ``CMAI_CULMINATION_AGE_YR``). The
# yield-curve *level* (Vmax), net price, harvest cost, and the treatment
# yield-effects are then fit by least squares so each (ecoclass,
# prescription) cell's max-PNV matches its Table 5.3 anchor.

from scipy.optimize import brentq, least_squares  # noqa: E402

from fresh_daugherty.instance.thesis import CMAI_CULMINATION_AGE_YR  # noqa: E402

#: Chapman-Richards shape parameter (shared; >1 gives an S-curve).
CR_SHAPE_M = 3.0


def k_for_culmination(culmination_age_yr: float, m: float = CR_SHAPE_M) -> float:
    """Chapman-Richards ``k`` whose MAI culminates at ``culmination_age_yr``."""

    def culm(k: float) -> float:
        a = np.linspace(1.0, 400.0, 4000)
        v = (1.0 - np.exp(-k * a)) ** m
        return a[int(np.argmax(v / a))]

    return float(brentq(lambda k: culm(k) - culmination_age_yr, 1e-4, 0.2))


#: Treatments that distinguish the prescriptions (thesis p.73). ``vm`` and
#: ``pct`` occur one period after planting; ``fert`` in the fourth period;
#: ``ct`` (commercial thinning) is a mid-rotation revenue. Prescription 1 is
#: natural regeneration (no planting cost); all others plant.
PRESCRIPTION_TREATMENTS: dict[Prescription, tuple[str, ...]] = {
    Prescription.NATURAL_REGEN: (),
    Prescription.PLANT: (),
    Prescription.PLANT_CT: ("ct",),
    Prescription.PLANT_VM_PCT: ("vm", "pct"),
    Prescription.PLANT_VM_PCT_FERT: ("vm", "pct", "fert"),
    Prescription.PLANT_VM_PCT_CT: ("vm", "pct", "ct"),
    Prescription.PLANT_VM_PCT_FERT_CT: ("vm", "pct", "fert", "ct"),
}

#: Treatment timings (years since the regenerated stand is established).
_TREATMENT_YEAR = {"vm": 10.0, "pct": 10.0, "fert": 40.0, "ct": 40.0}


class _CalibParams:
    """Flat vector <-> structured calibration parameters.

    Per-ecoclass economics (price, harvest cost, Vmax) — CM-CE is
    negatively-valued because its harvest cost exceeds its timber value — plus
    shared treatment yield-effects and the commercial-thinning revenue, and a
    natural-regeneration yield penalty (unstocked/understocked natural regen
    yields less than a planted stand).
    """

    def __init__(self, x: np.ndarray):
        n = len(_ECOCLASS_ORDER)
        self.price = dict(zip(_ECOCLASS_ORDER, x[0:n], strict=True))
        self.hcost = dict(zip(_ECOCLASS_ORDER, x[n : 2 * n], strict=True))
        self.vmax = dict(zip(_ECOCLASS_ORDER, x[2 * n : 3 * n], strict=True))
        self.treat_ym = dict(zip(("vm", "pct", "fert", "ct"), x[3 * n : 3 * n + 4], strict=True))
        self.ct_revenue = x[3 * n + 4]
        self.natural_regen_ym = x[3 * n + 5]


_ECOCLASS_ORDER = (Ecoclass.CH_CW, Ecoclass.CD_CP, Ecoclass.CR_CF, Ecoclass.CM_CE)


def _cell_model(eco: Ecoclass, rx: Prescription, p: _CalibParams) -> dict:
    """Build the per-cell model (yield curve, economics, intermediate flows)."""
    ymult = 1.0
    for t in PRESCRIPTION_TREATMENTS[rx]:
        ymult *= p.treat_ym[t]
    if rx is Prescription.NATURAL_REGEN:
        ymult *= p.natural_regen_ym
    yp = YieldParams(
        vmax=p.vmax[eco] * ymult,
        k=k_for_culmination(CMAI_CULMINATION_AGE_YR[eco]),
        m=CR_SHAPE_M,
    )
    econ = EconomicsParams(net_price_per_mcf=p.price[eco], harvest_cost_per_mcf=p.hcost[eco])
    inter: list[tuple[float, float]] = []
    if "ct" in PRESCRIPTION_TREATMENTS[rx]:
        # Commercial thinning: a mid-rotation revenue from the removed volume.
        inter.append((_TREATMENT_YEAR["ct"], p.ct_revenue))
    return {"yield": yp, "econ": econ, "intermediate": tuple(inter)}


def _cell_pnv_rotation(eco: Ecoclass, rx: Prescription, p: _CalibParams) -> tuple[float, float]:
    model = _cell_model(eco, rx, p)
    rng = ROTATION_RANGES[(eco, rx)]
    assert rng is not None
    return best_rotation(
        model["yield"],
        model["econ"],
        (rng.lo, rng.hi),
        intermediate_cash_flows=model["intermediate"],
    )


def _fit_residuals(x: np.ndarray) -> np.ndarray:
    p = _CalibParams(x)
    errs: list[float] = []
    for (eco, rx), anchor in PNV_ROTATION_ANCHORS.items():
        if anchor is None:
            continue
        opt_r, max_lev = _cell_pnv_rotation(eco, rx, p)
        # Fit PNV magnitude (scaled) primarily; rotation secondarily.
        errs.append((max_lev - anchor.max_pnv_per_ac) / 100.0)
        errs.append((opt_r - anchor.optimal_rotation_yr) / 25.0)
    return np.array(errs)


def calibrate() -> dict:
    """Calibrate the reconstruction to the Table 5.3 anchors (least squares).

    Populates and returns the per-cell model parameters. The yield-curve
    shapes are grounded in the Umpqua LRMP CMAI culmination ages; the levels
    and economics are fit to the thesis's Table 5.3 max-PNV/rotation anchors.
    """
    global _CALIBRATED
    n = len(_ECOCLASS_ORDER)
    # x = [price(4), hcost(4), Vmax(4), ym(vm,pct,fert,ct), ct_revenue,
    #      natural_regen_ym]
    x0 = np.array(
        [
            200.0,
            180.0,
            150.0,
            60.0,  # price per ecoclass
            90.0,
            95.0,
            100.0,
            200.0,  # harvest cost per ecoclass (CM-CE highest)
            30.0,
            22.0,
            18.0,
            12.0,  # Vmax per ecoclass
            1.1,
            1.1,
            1.25,
            1.1,  # treatment yield mults (vm, pct, fert, ct)
            300.0,  # commercial-thinning revenue
            0.8,  # natural-regen yield penalty
        ]
    )
    lb = np.array([20.0] * n + [30.0] * n + [5.0] * n + [1.0, 1.0, 1.0, 0.8] + [0.0] + [0.5])
    ub = np.array([600.0] * n + [400.0] * n + [60.0] * n + [1.6, 1.6, 2.5, 1.5] + [1500.0] + [1.0])
    sol = least_squares(_fit_residuals, x0, bounds=(lb, ub), max_nfev=6000)
    if not sol.success:
        raise RuntimeError(f"reconstruction calibration did not converge: {sol.message}")
    p = _CalibParams(sol.x)
    _CALIBRATED = {
        (eco, rx): _cell_model(eco, rx, p)
        for (eco, rx), anchor in PNV_ROTATION_ANCHORS.items()
        if anchor is not None
    }
    return _CALIBRATED


# Calibrated parameter set (populated by :func:`calibrate`).
_CALIBRATED: dict | None = None


def calibrated_params() -> dict:
    """Return the calibrated per-cell reconstruction parameters (runs the
    calibration on first call)."""
    global _CALIBRATED
    if _CALIBRATED is None:
        calibrate()
    return _CALIBRATED


__all__ = [
    "RECONSTRUCTION_ASSUMPTIONS",
    "EconomicsParams",
    "YieldParams",
    "best_rotation",
    "calibrate",
    "calibrated_params",
    "calibration_report",
    "escalated_price",
    "faustmann_lev",
    "k_for_culmination",
    "yield_volume",
]
