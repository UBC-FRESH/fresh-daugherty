"""Accessors over the extracted Umpqua FEIS data (real FORPLAN data).

The extracted records live in :mod:`fresh_daugherty.instance.umpqua_feis`
(auto-generated from the FEIS Appendix B OCR text). This module turns them
into the standing-volume-by-age yield curves and the economics the case-study
model uses.

Provenance: Umpqua National Forest FEIS Appendix B (HathiTrust record
002439528, public domain); the FORPLAN analysis volume. Yields are volumes
removed per entry (MCF/ac); the regeneration-harvest volume at age R is the
standing volume at R (clearcut, or 75% for shelterwood with 25% the next
decade).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fresh_daugherty.instance.thesis import Ecoclass, Prescription
from fresh_daugherty.instance.umpqua_feis import (
    DF_PRICE_DIAMETER,
    SITE_INDEX_BY_ECOCLASS,
    SPECIES_ECONOMICS,
    UMPQUA_YIELD_TABLES,
)


def yield_tables_for(ecoclass: Ecoclass) -> list[dict]:
    """Return the extracted yield tables for an ecoclass (both emphases)."""
    code = ecoclass.value
    return [t for t in UMPQUA_YIELD_TABLES if t.get("ecoclass") == code]


def standing_volume_curve(
    ecoclass: Ecoclass,
    *,
    emphasis: str = "volume",
    table_index: int = 0,
) -> dict[int, float]:
    """Standing volume (MCF/ac) by age for an ecoclass's yield table.

    Uses the regeneration-harvest entries (the standing volume removed at a
    clearcut at that age). ``emphasis`` selects the volume-emphasis (first
    column group) or PNV-emphasis (second column group) values.
    """
    tables = yield_tables_for(ecoclass)
    if not tables:
        raise ValueError(f"no yield tables for ecoclass {ecoclass.value}")
    table = tables[table_index % len(tables)]
    offset = 0 if emphasis == "volume" else 3
    curve: dict[int, float] = {}
    for entry in table["entries"]:
        if entry["kind"] != "Regen":
            continue
        vals = entry["values"]
        if len(vals) > offset and vals[offset] is not None:
            curve[entry["age"]] = float(vals[offset])
    return curve


#: Thesis prescription -> FEIS yield-table treatment-combo keyword (the
#: most-intensive matching table). The FEIS "genetics" (improved stock) folds
#: into the thesis's planting; the thesis's vegetation-management (VM) maps to
#: the FEIS's improved-stock/intensive handling.
_RX_TABLE_KEYWORDS: dict[Prescription, tuple[str, ...]] = {
    Prescription.PLANT_VM_PCT_FERT_CT: (
        "Genetics, Precommercial Thin, Fertilizer, and Commercial Thin",
    ),
    Prescription.PLANT_VM_PCT_FERT: ("Genetics, Precommercial Thin, and Fertilizer",),
    Prescription.PLANT_VM_PCT_CT: ("Genetics, Precommercial Thin, and Commercial Thin",),
    Prescription.PLANT_VM_PCT: ("Genetics and Precommercial Thin",),
    Prescription.PLANT_CT: (
        "Precommercial Thin and Commercial Thin",
        "Precommercial Thin, and Commercial Thin",
    ),
    Prescription.PLANT: ("Precommercial Thin Only",),
    Prescription.NATURAL_REGEN: ("Precommercial Thin Only",),  # closest available
}


def real_yield_table(ecoclass: Ecoclass, prescription: Prescription) -> dict | None:
    """Return the FEIS yield table matching an (ecoclass, prescription)."""
    cands = yield_tables_for(ecoclass)
    if not cands:
        return None
    for kw in _RX_TABLE_KEYWORDS.get(prescription, ()):
        for t in cands:
            if kw in t["title"]:
                return t
    return cands[0]


def real_yield_curve(
    ecoclass: Ecoclass,
    prescription: Prescription,
    *,
    max_age: int = 220,
    emphasis: str = "volume",
) -> dict[int, float]:
    """Interpolated standing-volume (MCF/ac) by age curve from the real table.

    The FEIS regen-harvest volumes give standing volume at the tabled ages;
    this linearly interpolates to a 10-year grid and extends the curve flat
    past the last tabled age (over-mature). Returns {age: MCF/ac}.
    """
    table = real_yield_table(ecoclass, prescription)
    if table is None:
        raise ValueError(f"no FEIS yield table for {ecoclass.value} rx{int(prescription)}")
    offset = 0 if emphasis == "volume" else 3
    pts = {
        e["age"]: float(e["values"][offset])
        for e in table["entries"]
        if e["kind"] == "Regen" and len(e["values"]) > offset and e["values"][offset] is not None
    }
    if not pts:
        raise ValueError(f"FEIS table {table['table']} has no regen volumes")
    ages = sorted(pts)
    grid = np.arange(0, max_age + 1, 10)
    # Interpolate between tabled ages; hold flat below the first / above the last.
    vols = np.interp(grid, ages, [pts[a] for a in ages])
    return {int(a): float(v) for a, v in zip(grid, vols, strict=True)}


def mature_volume_crosscheck() -> pd.DataFrame:
    """Independent cross-check on the mature-type volumes.

    The case study's mature (existing over-mature) volumes are back-computed
    from the thesis's Table 5.4 PNV anchors (``model.mature_volume_mcf``), so
    matching Table 5.4 is *by construction*, not independent validation. This
    function compares those back-computed volumes against an **independent**
    source — the FEIS standing-volume-by-age curves evaluated at each mature
    type's age — to check they are at least the same order of magnitude.

    Returns a DataFrame with the back-computed volume, the independent FEIS
    volume, and their ratio per mature type.
    """
    from fresh_daugherty.instance.thesis import MATURE_TYPE_PNV

    rows = []
    for mt in MATURE_TYPE_PNV:
        net = real_ecoclass_net_revenue(mt.ecoclass)
        backcalc = mt.pnv_period1_per_ac / net if net > 0 else float("nan")
        curve = standing_volume_curve(mt.ecoclass)
        ages = sorted(curve)
        feis = float(np.interp(mt.age_yr, ages, [curve[a] for a in ages])) if ages else float("nan")
        rows.append(
            {
                "ecoclass": mt.ecoclass.value,
                "vegetation_type": mt.vegetation_type,
                "age_yr": mt.age_yr,
                "pnv_period1_per_ac": mt.pnv_period1_per_ac,
                "net_price_per_mcf": net,
                "backcalc_volume_mcf": backcalc,
                "feis_volume_mcf": feis,
                "ratio_feis_over_backcalc": (feis / backcalc)
                if backcalc == backcalc
                else float("nan"),
            }
        )
    return pd.DataFrame(rows)


#: Predominant species per ecoclass (thesis Table 5.1), mapped to FEIS species.
ECOCLASS_SPECIES: dict[Ecoclass, tuple[str, ...]] = {
    Ecoclass.CH_CW: ("Douglas-Fir", "Western Hemlock"),
    Ecoclass.CD_CP: ("Douglas-Fir", "Ponderosa Pine"),
    Ecoclass.CR_CF: ("Shasta (Noble) Fir", "Douglas-Fir"),
    Ecoclass.CM_CE: ("Mountain Hemlock", "Lodgepole Pine"),
}

#: Per-ecoclass access (road) cost ($/MCF), the cost that makes CM-CE
#: negatively valued (high-elevation, long-yard/road access). Documented
#: reconstruction value; FEIS road-cost tables (B-94..B-97) are the reference.
ECOCLASS_ACCESS_COST_PER_MCF: dict[Ecoclass, float] = {
    Ecoclass.CH_CW: 200.0,
    Ecoclass.CD_CP: 250.0,
    Ecoclass.CR_CF: 300.0,
    Ecoclass.CM_CE: 500.0,  # high-elevation access: the negatively-valued driver
}


def real_ecoclass_net_revenue(ecoclass: Ecoclass) -> float:
    """Net revenue ($/MCF) for an ecoclass from the FEIS species economics.

    The stumpage value ($/MBF, FEIS Table B-65) is the standing-timber value
    net of logging/manufacturing; converted to $/MCF by the species BF/CF
    factor and averaged over the ecoclass's predominant species, less the
    per-ecoclass access (road) cost. CM-CE's high access cost makes it
    negatively valued (the thesis's negatively-valued stratum).
    """
    spp = ECOCLASS_SPECIES[ecoclass]
    vals = []
    for sp in spp:
        stumpage, _log, _mfg, bfcf, _dbh = SPECIES_ECONOMICS[sp]
        vals.append(stumpage * bfcf)
    gross = sum(vals) / len(vals)
    return gross - ECOCLASS_ACCESS_COST_PER_MCF[ecoclass]


def model_lev(
    ecoclass: Ecoclass, prescription: Prescription, *, max_age: int = 200
) -> tuple[int, float]:
    """The model's max Faustmann LEV ($/ac) + optimal rotation for a cell.

    Computed from the real FEIS yield curve and the real per-ecoclass net
    revenue (stumpage less access cost) at the thesis 4% discount rate. This
    is the exact-vintage validation against the thesis's Table 5.3 anchors.
    """
    from fresh_daugherty.instance.thesis import ROTATION_RANGES, THESIS_DISCOUNT_RATE

    curve = real_yield_curve(ecoclass, prescription, max_age=max_age)
    net = real_ecoclass_net_revenue(ecoclass)
    rng = ROTATION_RANGES[(ecoclass, prescription)]
    assert rng is not None
    best_r, best_lev = rng.lo, -np.inf
    for r in range(rng.lo, rng.hi + 1):
        vol = curve.get(min(r, max_age), 0.0)
        npv = net * vol * np.exp(-THESIS_DISCOUNT_RATE * r)
        lev = npv / (1.0 - np.exp(-THESIS_DISCOUNT_RATE * r))
        if lev > best_lev:
            best_r, best_lev = r, lev
    return best_r, float(best_lev)


__all__ = [
    "DF_PRICE_DIAMETER",
    "ECOCLASS_ACCESS_COST_PER_MCF",
    "ECOCLASS_SPECIES",
    "SITE_INDEX_BY_ECOCLASS",
    "SPECIES_ECONOMICS",
    "UMPQUA_YIELD_TABLES",
    "model_lev",
    "real_ecoclass_net_revenue",
    "real_yield_curve",
    "real_yield_table",
    "standing_volume_curve",
    "yield_tables_for",
]
