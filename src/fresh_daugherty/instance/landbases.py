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
from fresh_daugherty.model import ecoclass_code, mature_rx

#: Documented construction assumptions for the landbases (thesis pp. 78-80,
#: Table 5.5). Rebuilt in P16.4 (#95) to follow the p. 79 text; the earlier
#: construction put CM-CE in landbases 9-18 and ignored the p. 79 detail.
LANDBASE_ASSUMPTIONS: tuple[str, ...] = (
    "Landbase 1 (all mature) splits the 10,000 ac evenly across the five "
    "mature vegetation types (Table 5.4); the thesis does not give the split.",
    "Landbase 2 is landbase 1 with the CM-CE mature type excluded and the "
    "area redistributed evenly across the remaining four (p. 79).",
    "Landbases 3-8 are landbase 1/2 after 40 or 70 years of area-control "
    "harvest at a 100- or 70-year rotation (Table 5.5): a fixed area "
    "(total * period / rotation) per decade (p. 79: roughly one-tenth or "
    "one-seventh), taken from the highest-volume stands first (p. 79).",
    "Landbases 3-6: harvested area regenerates under prescriptions 1 and 2 "
    "only (p. 79: reforestation only); prescription 1 (natural regeneration) "
    "is viable only on CR-CF (p. 74), so CR-CF regenerates half to 1 and half "
    "to 2 and the other ecoclasses to 2 (split assumed).",
    "Landbases 7-8 (p. 79: the managed forests resulting from the scenarios "
    "of landbases 5 and 6): area harvested in the last 30 years received "
    "early cultural treatments, modelled as prescription 4 (vegetation "
    "management and precommercial thinning one period after planting, p. 73); "
    "earlier harvests regenerate as in landbases 3-6.",
    "Landbases 9-18 contain no CM-CE (p. 79).",
    "Landbase 9: half CH-CW, a quarter each CD-CP and CR-CF; equal acres in "
    "all age classes (10-120 yr); 'the most intensive prescriptions, divided "
    "equally between regimes with and without thinning' (p. 79) read as "
    "prescriptions 5 and 7 (fertilized, without/with commercial thinning) on "
    "CH-CW and CD-CP, and 4 and 6 on CR-CF, where fertilization is not "
    "available (p. 73).",
    "Landbase 10: the ecoclass shares and prescriptions of landbase 9 with an "
    "irregular age-class distribution (p. 79), drawn once from a uniform "
    "distribution with a fixed seed.",
    "Landbases 11-18: uniform random acres over (ecoclass, prescription, age "
    "class) cells, scaled so each management intensity gets equal acres on "
    "average (p. 79); one seed-fixed draw per landbase (seed 42 + id).",
)

#: Age classes (yr) of the young-growth landbases 9-18 (up to ~rotation).
YOUNG_AGES: tuple[int, ...] = tuple(range(10, 130, 10))
#: Ecoclass shares of landbases 9 and 10 (p. 79).
LANDBASE_9_SHARES: dict[Ecoclass, float] = {
    Ecoclass.CH_CW: 0.5,
    Ecoclass.CD_CP: 0.25,
    Ecoclass.CR_CF: 0.25,
}
#: The most intensive prescriptions, without and with commercial thinning.
INTENSIVE_RX: dict[Ecoclass, tuple[Prescription, Prescription]] = {
    Ecoclass.CH_CW: (Prescription.PLANT_VM_PCT_FERT, Prescription.PLANT_VM_PCT_FERT_CT),
    Ecoclass.CD_CP: (Prescription.PLANT_VM_PCT_FERT, Prescription.PLANT_VM_PCT_FERT_CT),
    Ecoclass.CR_CF: (Prescription.PLANT_VM_PCT, Prescription.PLANT_VM_PCT_CT),
}
LANDBASE_10_SEED = 10


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
                "rx": mature_rx(mt),
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
                "rx": mature_rx(mt),
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


def _young_row(eco: Ecoclass, rx: Prescription, age: int, area: float) -> dict:
    return {
        "forest": "umpqua",
        "ecoclass": ecoclass_code(eco),
        "rx": f"rx{int(rx)}",
        "origin": "regenerated",
        "state": "baseline",
        "age": age,
        "area_ac": area,
    }


def young_growth(equal: bool = True) -> pd.DataFrame:
    """Landbase 9 (equal acres by age class) / 10 (irregular ages): intensively
    managed young growth without CM-CE (p. 79; see ``LANDBASE_ASSUMPTIONS``)."""
    rng = None if equal else np.random.default_rng(LANDBASE_10_SEED)
    rows = []
    for eco, share in LANDBASE_9_SHARES.items():
        for rx in INTENSIVE_RX[eco]:
            cell_area = LANDBASE_ACRES * share / len(INTENSIVE_RX[eco])
            w = np.ones(len(YOUNG_AGES)) if rng is None else rng.random(len(YOUNG_AGES))
            w = w / w.sum()
            rows += [
                _young_row(eco, rx, a, cell_area * x) for a, x in zip(YOUNG_AGES, w, strict=True)
            ]
    return _areas(rows)


def random_young_growth(seed: int) -> pd.DataFrame:
    """Landbases 11-18: randomly generated young growth without CM-CE (p. 79).

    Uniform random weights over (ecoclass, prescription, age class) cells,
    each divided by the number of ecoclasses offering that prescription, so
    every management intensity receives equal acres on average."""
    rng = np.random.default_rng(seed)
    cells = [(e, r) for (e, r) in _managed_cells() if e is not Ecoclass.CM_CE]
    n_eco = {r: sum(1 for (_e, rr) in cells if rr == r) for (_e, r) in cells}
    combos = [(eco, rx, age) for (eco, rx) in cells for age in YOUNG_AGES]
    weights = rng.random(len(combos)) / np.array([n_eco[rx] for (_e, rx, _a) in combos])
    weights = weights / weights.sum()
    return _areas(
        [
            _young_row(eco, rx, age, LANDBASE_ACRES * w)
            for (eco, rx, age), w in zip(combos, weights, strict=True)
        ]
    )


def _mature_volume_per_ac() -> dict[tuple[str, str], float]:
    """Standing volume (MCF/ac) of each mature type, keyed (ecoclass, rx code)."""
    from fresh_daugherty.instance.feis import real_ecoclass_net_revenue
    from fresh_daugherty.model import mature_volume_mcf

    return {
        (ecoclass_code(mt.ecoclass), mature_rx(mt)): mature_volume_mcf(
            mt, real_ecoclass_net_revenue(mt.ecoclass)
        )
        for mt in MATURE_TYPE_PNV
    }


def _regeneration_rx(ecoclass: str, years_before_present: int) -> list[tuple[str, float]]:
    """Prescriptions (with area shares) for area harvested ``years_before_present``
    years ago under the area-control history (``LANDBASE_ASSUMPTIONS``)."""
    if years_before_present <= 30:
        return [(f"rx{int(Prescription.PLANT_VM_PCT)}", 1.0)]
    if ecoclass == ecoclass_code(Ecoclass.CR_CF):
        return [
            (f"rx{int(Prescription.NATURAL_REGEN)}", 0.5),
            (f"rx{int(Prescription.PLANT)}", 0.5),
        ]
    return [(f"rx{int(Prescription.PLANT)}", 1.0)]


def area_control_derived(
    base_id: int, years: int, rotation: int, *, cultural_treatments: bool = False
) -> pd.DataFrame:
    """Landbase ``base_id`` (1 or 2) after ``years`` of area-control harvest at
    ``rotation`` (Table 5.5): a fixed area per decade, highest-volume mature
    stands first (p. 79), regenerated at age 0 under prescriptions 1/2 or, with
    ``cultural_treatments`` (landbases 7-8), prescription 4 for area harvested in
    the last 30 years. Unharvested area ages. See ``LANDBASE_ASSUMPTIONS``."""
    base = landbase_1() if base_id == 1 else landbase_2()
    stands = [dict(r) for r in base.to_dict("records")]
    volume = _mature_volume_per_ac()
    area_per_period = LANDBASE_ACRES * PERIOD_LENGTH_YEARS / rotation
    n_periods = years // PERIOD_LENGTH_YEARS
    for k in range(n_periods):
        years_before_present = (n_periods - k) * PERIOD_LENGTH_YEARS
        mature = [r for r in stands if r["origin"] == "existing" and r["area_ac"] > 0]
        mature.sort(key=lambda r: -volume[(r["ecoclass"], r["rx"])])
        to_harvest = area_per_period
        new = []
        for r in mature:
            if to_harvest <= 1e-9:
                break
            take = min(r["area_ac"], to_harvest)
            r["area_ac"] -= take
            to_harvest -= take
            rx_split = (
                _regeneration_rx(r["ecoclass"], years_before_present)
                if cultural_treatments
                else _regeneration_rx(r["ecoclass"], 10**6)
            )
            for rx_code, share in rx_split:
                new.append(
                    {
                        "forest": r["forest"],
                        "ecoclass": r["ecoclass"],
                        "rx": rx_code,
                        "origin": "regenerated",
                        "state": r["state"],
                        "age": 0,
                        "area_ac": take * share,
                    }
                )
        if to_harvest > 1e-6:
            raise ValueError(f"area control ran out of mature area in decade {k + 1}")
        stands += new
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
        return area_control_derived(1, years=70, rotation=70, cultural_treatments=True)
    if landbase_id == 8:
        return area_control_derived(2, years=70, rotation=70, cultural_treatments=True)
    if landbase_id == 9:
        return young_growth(equal=True)
    if landbase_id == 10:
        return young_growth(equal=False)
    if 11 <= landbase_id <= 18:
        return random_young_growth(seed + landbase_id)
    raise NotImplementedError(f"landbase {landbase_id} not in 1-18")


__all__ = [
    "INTENSIVE_RX",
    "LANDBASE_9_SHARES",
    "LANDBASE_ASSUMPTIONS",
    "YOUNG_AGES",
    "area_control_derived",
    "landbase_1",
    "landbase_2",
    "landbase_areas",
    "random_young_growth",
    "young_growth",
]
