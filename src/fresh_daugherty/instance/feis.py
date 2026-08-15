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

from fresh_daugherty.instance.thesis import Ecoclass
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


__all__ = [
    "DF_PRICE_DIAMETER",
    "SITE_INDEX_BY_ECOCLASS",
    "SPECIES_ECONOMICS",
    "UMPQUA_YIELD_TABLES",
    "standing_volume_curve",
    "yield_tables_for",
]
