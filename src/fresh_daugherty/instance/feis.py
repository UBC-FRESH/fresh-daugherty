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
    return {int(a): float(v) for a, v in zip(grid, vols)}


__all__ = [
    "DF_PRICE_DIAMETER",
    "SITE_INDEX_BY_ECOCLASS",
    "SPECIES_ECONOMICS",
    "UMPQUA_YIELD_TABLES",
    "real_yield_curve",
    "real_yield_table",
    "standing_volume_curve",
    "yield_tables_for",
]
