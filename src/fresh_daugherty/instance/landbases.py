"""Initial forest conditions (the 18 landbases, Table 5.5) for the case-study.

Each landbase covers 10,000 acres. The structured landbases are constructed
from the case-study strata; the "after N years of area-control harvest"
landbases (3-8) and the randomly-generated young-growth landbases (11-18) are
produced by documented construction rules (recorded in the module constant).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fresh_daugherty.instance.reconstruct import calibrated_params
from fresh_daugherty.instance.thesis import (
    LANDBASE_ACRES,
    MATURE_TYPE_PNV,
    PERIOD_LENGTH_YEARS,
    Ecoclass,
    Prescription,
)
from fresh_daugherty.model import MATURE_RX, ecoclass_code

#: Documented construction assumptions for the landbases.
LANDBASE_ASSUMPTIONS: tuple[str, ...] = (
    "Landbase 1 (all mature) splits the 10,000 ac evenly across the five "
    "mature vegetation types (Table 5.4); the thesis does not give the split.",
    "Landbase 2 is landbase 1 with the CM-CE mature type excluded and the "
    "area redistributed across the remaining four.",
    "Young-growth landbases (9, 10) distribute area across the managed "
    "(ecoclass, prescription) cells; 9 uses equal acres per age class, 10 an "
    "unequal (declining-with-age) distribution.",
    "Landbases 3-8 derive landbase 1/2 after 40 or 70 years of area-control "
    "harvest (70- or 100-yr rotation): a fixed area (total*period/rotation) "
    "harvested oldest-first each period, regenerated to the base PLANT "
    "prescription of the same ecoclass at age 0 (the thesis does not give the "
    "within-period detail; these are documented reconstruction choices).",
    "Landbases 11-18 (random young-growth) are generated seed-fixed.",
)


def _areas(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(
        rows, columns=["forest", "ecoclass", "rx", "origin", "state", "age", "area_ac"]
    )


def landbase_1() -> pd.DataFrame:
    """Landbase 1: all mature existing stands (5 mature types, even split)."""
    per = LANDBASE_ACRES / len(MATURE_TYPE_PNV)
    return _areas(
        [
            {
                "forest": "umpqua",
                "ecoclass": ecoclass_code(mt.ecoclass),
                "rx": MATURE_RX,
                "origin": "existing",
                "state": "baseline",
                "age": mt.age_yr,
                "area_ac": per,
            }
            for mt in MATURE_TYPE_PNV
        ]
    )


def landbase_2() -> pd.DataFrame:
    """Landbase 2: all mature existing stands, CM-CE excluded."""
    types = [mt for mt in MATURE_TYPE_PNV if mt.ecoclass is not Ecoclass.CM_CE]
    per = LANDBASE_ACRES / len(types)
    return _areas(
        [
            {
                "forest": "umpqua",
                "ecoclass": ecoclass_code(mt.ecoclass),
                "rx": MATURE_RX,
                "origin": "existing",
                "state": "baseline",
                "age": mt.age_yr,
                "area_ac": per,
            }
            for mt in types
        ]
    )


def _managed_cells() -> list[tuple[Ecoclass, Prescription]]:
    params = calibrated_params()
    return [(eco, rx) for (eco, rx) in params]


def young_growth(equal: bool = True) -> pd.DataFrame:
    """Landbase 9 (equal) / 10 (unequal): young-growth under intensive management.

    A *regulated* young-growth forest: each managed (ecoclass, prescription)
    cell has area spread across age classes from young up to the rotation age,
    so the forest has harvestable (mature) volume every period. Landbase 9 uses
    equal acres per age class; landbase 10 an unequal (declining-with-age)
    distribution.
    """
    cells = _managed_cells()
    ages = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]  # up to ~rotation
    rows = []
    combos = [(eco, rx, age) for (eco, rx) in cells for age in ages]
    weights = (
        np.ones(len(combos))
        if equal
        else np.array([1.0 / (1 + a) for (_e, _r, a) in combos])  # declining with age
    )
    weights = weights / weights.sum()
    for (eco, rx, age), w in zip(combos, weights, strict=True):
        rows.append(
            {
                "forest": "umpqua",
                "ecoclass": ecoclass_code(eco),
                "rx": f"rx{int(rx)}",
                "origin": "regenerated",
                "state": "baseline",
                "age": age,
                "area_ac": LANDBASE_ACRES * w,
            }
        )
    return _areas(rows)


def random_young_growth(seed: int) -> pd.DataFrame:
    """Landbases 11-18: randomly generated young-growth (seed-fixed).

    Ages span up to the rotation range (as the structured young-growth
    landbases 9/10 do), so the forest has period-1 operable volume. (An earlier
    version used only ages 10-40, below the rotation minimum, so period-1
    harvest was zero and a symmetric flow constraint pinned the whole
    trajectory to zero---a corner artifact, now fixed.)"""
    rng = np.random.default_rng(seed)
    cells = _managed_cells()
    ages = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    combos = [(eco, rx, age) for (eco, rx) in cells for age in ages]
    weights = rng.random(len(combos))
    weights = weights / weights.sum()
    rows = []
    for (eco, rx, age), w in zip(combos, weights, strict=True):
        rows.append(
            {
                "forest": "umpqua",
                "ecoclass": ecoclass_code(eco),
                "rx": f"rx{int(rx)}",
                "origin": "regenerated",
                "state": "baseline",
                "age": age,
                "area_ac": LANDBASE_ACRES * w,
            }
        )
    return _areas(rows)


def area_control_derived(
    base_id: int,
    years: int,
    rotation: int,
    *,
    regenerate_rx: Prescription = Prescription.PLANT,
) -> pd.DataFrame:
    """Derive a landbase after ``years`` of area-control harvest (thesis Table 5.5).

    Landbases 3-8 are landbase 1 or 2 "after N years of harvest using area
    control" at a given rotation. Area control harvests a fixed *area* per
    period (total_area * period_length / rotation), oldest stands first,
    regenerating each harvested area to the base managed prescription at age 0;
    unharvested area ages. This converts part of the over-mature forest into a
    disequilibrium->regulation gradient of regenerated cohorts.

    Documented assumptions (the thesis does not give the within-period detail):
    oldest-first harvest order; regeneration to the base PLANT prescription of
    the same ecoclass; area-control rate = total_area * period_length /
    rotation per period.
    """
    base = landbase_1() if base_id == 1 else landbase_2()
    stands = [dict(r) for r in base.to_dict("records")]
    area_per_period = LANDBASE_ACRES * PERIOD_LENGTH_YEARS / rotation
    rx_code = f"rx{int(regenerate_rx)}"
    for _ in range(years // PERIOD_LENGTH_YEARS):
        # Harvest oldest-first, a fixed area this period.
        stands.sort(key=lambda r: -r["age"])
        to_harvest = area_per_period
        for r in stands:
            if to_harvest <= 0:
                break
            take = min(r["area_ac"], to_harvest)
            if take <= 0:
                continue
            r["area_ac"] -= take
            to_harvest -= take
            # Regenerate the harvested area to the managed prescription, age 0.
            stands.append(
                {
                    "forest": r["forest"],
                    "ecoclass": r["ecoclass"],
                    "rx": rx_code,
                    "origin": "regenerated",
                    "state": r["state"],
                    "age": 0,
                    "area_ac": take,
                }
            )
        # Age all remaining stands one period.
        for r in stands:
            r["age"] += PERIOD_LENGTH_YEARS
    return _areas([r for r in stands if r["area_ac"] > 1e-6])


def landbase_areas(landbase_id: int, *, seed: int = 42) -> pd.DataFrame:
    """Return the initial area records for landbase ``landbase_id``."""
    if landbase_id == 1:
        return landbase_1()
    if landbase_id == 2:
        return landbase_2()
    # Landbases 3-8: landbase 1/2 after N years of area-control harvest (Table 5.5).
    if landbase_id == 3:
        return area_control_derived(1, years=40, rotation=100)
    if landbase_id == 4:
        return area_control_derived(2, years=40, rotation=100)
    if landbase_id == 5:
        return area_control_derived(1, years=40, rotation=70)
    if landbase_id == 6:
        return area_control_derived(2, years=40, rotation=70)
    if landbase_id == 7:
        return area_control_derived(1, years=70, rotation=70)
    if landbase_id == 8:
        return area_control_derived(2, years=70, rotation=70)
    if landbase_id == 9:
        return young_growth(equal=True)
    if landbase_id == 10:
        return young_growth(equal=False)
    if 11 <= landbase_id <= 18:
        return random_young_growth(seed + landbase_id)
    raise NotImplementedError(f"landbase {landbase_id} not in 1-18")


__all__ = [
    "LANDBASE_ASSUMPTIONS",
    "area_control_derived",
    "landbase_1",
    "landbase_2",
    "landbase_areas",
    "random_young_growth",
    "young_growth",
]
