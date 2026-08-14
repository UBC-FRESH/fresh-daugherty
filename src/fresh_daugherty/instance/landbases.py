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

    Distributes the landbase across the managed (ecoclass, prescription) cells
    at a spread of young ages.
    """
    cells = _managed_cells()
    ages = [10, 20, 30, 40]
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
    """Landbases 11-18: randomly generated young-growth (seed-fixed)."""
    rng = np.random.default_rng(seed)
    cells = _managed_cells()
    ages = [10, 20, 30, 40]
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


def landbase_areas(landbase_id: int, *, seed: int = 42) -> pd.DataFrame:
    """Return the initial area records for landbase ``landbase_id``."""
    if landbase_id == 1:
        return landbase_1()
    if landbase_id == 2:
        return landbase_2()
    if landbase_id == 9:
        return young_growth(equal=True)
    if landbase_id == 10:
        return young_growth(equal=False)
    if 11 <= landbase_id <= 18:
        return random_young_growth(seed + landbase_id)
    raise NotImplementedError(
        f"landbase {landbase_id} (3-8 are area-control-harvest-derived) is not "
        "yet constructed; see LANDBASE_ASSUMPTIONS"
    )


__all__ = [
    "LANDBASE_ASSUMPTIONS",
    "landbase_1",
    "landbase_2",
    "landbase_areas",
    "random_young_growth",
    "young_growth",
]
