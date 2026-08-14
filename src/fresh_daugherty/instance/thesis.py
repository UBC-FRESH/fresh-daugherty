"""Transcribed Daugherty (1991) case-study reference data (thesis Tables 5.1-5.5).

These records are transcribed verbatim from the scanned thesis (the scan is
held locally in the fresh-fuchs repo at `tmp/daugherty1991credibility.pdf`;
it is not redistributable and is never tracked). They are the *anchors* the
case-study reconstruction is calibrated against.

The raw per-age yield curves, per-stratum initial areas, and detailed
price/cost tables are NOT in the thesis (they are in the archival USDA 1987
Umpqua Forest Plan Draft EIS); they are reconstructed in
:mod:`fresh_daugherty.instance.reconstruct` under documented assumptions.

Provenance for every record: source = Daugherty (1991) ch. 5; the printed
thesis page is recorded per table.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum

from pydantic import BaseModel, Field

#: Planning horizon: 150 years in 15 equal (10-year) periods (thesis p.71).
HORIZON_YEARS = 150
N_PERIODS = 15
PERIOD_LENGTH_YEARS = 10

#: Timber volumes are measured in thousand cubic feet (thesis p.72).
VOLUME_UNIT = "MCF"  # thousand cubic feet

#: Thesis discount rate for the PNV anchors (Table 5.3 header, p.75): 4%.
THESIS_DISCOUNT_RATE = 0.04

#: Delivered log prices rise at a real 1%/yr for the first 50 years, then are
#: constant (thesis p.74); logging costs rise at the same rate, so the real
#: stumpage price rises 1%/yr for the first 50 years.
PRICE_ESCALATION_RATE = 0.01
PRICE_ESCALATION_YEARS = 50


class Ecoclass(StrEnum):
    """The four ecoclass groups, in descending order of growth potential.

    (Thesis Table 5.1, p.72.)
    """

    CH_CW = "CH-CW"  # moist warm site; Douglas-fir + western hemlock
    CD_CP = "CD-CP"  # hot dry site; Douglas-fir (+ ponderosa pine)
    CR_CF = "CR-CF"  # between hemlock zones; Shasta red fir + Douglas-fir
    CM_CE = "CM-CE"  # high-elevation moist; mountain hemlock + lodgepole pine


class Prescription(IntEnum):
    """The seven silvicultural prescriptions (management intensity levels).

    (Thesis p.73.) Timing: vegetation management + precommercial thinning one
    period after planting; fertilization in the fourth period after planting.
    """

    NATURAL_REGEN = 1  # natural regeneration, final harvest
    PLANT = 2  # plant, final harvest
    PLANT_CT = 3  # plant, commercial thinning, final harvest
    PLANT_VM_PCT = 4  # plant, vegetation mgmt, precommercial thin, final harvest
    PLANT_VM_PCT_FERT = 5  # + fertilization, final harvest
    PLANT_VM_PCT_CT = 6  # + commercial thinning, final harvest
    PLANT_VM_PCT_FERT_CT = 7  # + fertilization + commercial thinning, final harvest


class RotationRange(BaseModel):
    """Allowed final-harvest (rotation) age range in years (Table 5.2)."""

    lo: int
    hi: int


#: Table 5.2 (p.73): rotation-age choices (years) by ecoclass x prescription.
#: ``None`` = prescription N/A for that ecoclass.
ROTATION_RANGES: dict[tuple[Ecoclass, Prescription], RotationRange | None] = {
    (Ecoclass.CH_CW, Prescription.NATURAL_REGEN): None,
    (Ecoclass.CH_CW, Prescription.PLANT): RotationRange(lo=60, hi=150),
    (Ecoclass.CH_CW, Prescription.PLANT_CT): RotationRange(lo=100, hi=180),
    (Ecoclass.CH_CW, Prescription.PLANT_VM_PCT): RotationRange(lo=70, hi=150),
    (Ecoclass.CH_CW, Prescription.PLANT_VM_PCT_FERT): RotationRange(lo=60, hi=150),
    (Ecoclass.CH_CW, Prescription.PLANT_VM_PCT_CT): RotationRange(lo=70, hi=150),
    (Ecoclass.CH_CW, Prescription.PLANT_VM_PCT_FERT_CT): RotationRange(lo=60, hi=150),
    (Ecoclass.CD_CP, Prescription.NATURAL_REGEN): None,
    (Ecoclass.CD_CP, Prescription.PLANT): RotationRange(lo=70, hi=150),
    (Ecoclass.CD_CP, Prescription.PLANT_CT): RotationRange(lo=120, hi=180),
    (Ecoclass.CD_CP, Prescription.PLANT_VM_PCT): RotationRange(lo=80, hi=150),
    (Ecoclass.CD_CP, Prescription.PLANT_VM_PCT_FERT): RotationRange(lo=70, hi=150),
    (Ecoclass.CD_CP, Prescription.PLANT_VM_PCT_CT): RotationRange(lo=80, hi=150),
    (Ecoclass.CD_CP, Prescription.PLANT_VM_PCT_FERT_CT): RotationRange(lo=80, hi=150),
    (Ecoclass.CR_CF, Prescription.NATURAL_REGEN): RotationRange(lo=80, hi=150),
    (Ecoclass.CR_CF, Prescription.PLANT): RotationRange(lo=80, hi=150),
    (Ecoclass.CR_CF, Prescription.PLANT_CT): None,
    (Ecoclass.CR_CF, Prescription.PLANT_VM_PCT): RotationRange(lo=80, hi=150),
    (Ecoclass.CR_CF, Prescription.PLANT_VM_PCT_FERT): None,
    (Ecoclass.CR_CF, Prescription.PLANT_VM_PCT_CT): RotationRange(lo=80, hi=150),
    (Ecoclass.CR_CF, Prescription.PLANT_VM_PCT_FERT_CT): None,
    (Ecoclass.CM_CE, Prescription.NATURAL_REGEN): None,
    (Ecoclass.CM_CE, Prescription.PLANT): RotationRange(lo=110, hi=190),
    (Ecoclass.CM_CE, Prescription.PLANT_CT): None,
    (Ecoclass.CM_CE, Prescription.PLANT_VM_PCT): RotationRange(lo=110, hi=190),
    (Ecoclass.CM_CE, Prescription.PLANT_VM_PCT_FERT): None,
    (Ecoclass.CM_CE, Prescription.PLANT_VM_PCT_CT): RotationRange(lo=120, hi=200),
    (Ecoclass.CM_CE, Prescription.PLANT_VM_PCT_FERT_CT): None,
}


class PnvRotationAnchor(BaseModel):
    """Highest-PNV anchor for an (ecoclass, prescription).

    Max present net value ($/ac, 4% discount) at the optimal rotation age
    (years). Table 5.3 (p.75). Values are exclusive of reforestation cost
    (PNV of the prescription for an existing stratum established one decade
    before the horizon).
    """

    max_pnv_per_ac: float
    optimal_rotation_yr: int


#: Table 5.3 (p.75): max PNV ($/ac, 4%) and optimal rotation (yr) by
#: ecoclass x prescription. ``None`` = N/A. Negative values are the
#: negatively-valued strata (CM-CE).
PNV_ROTATION_ANCHORS: dict[tuple[Ecoclass, Prescription], PnvRotationAnchor | None] = {
    (Ecoclass.CH_CW, Prescription.NATURAL_REGEN): None,
    (Ecoclass.CH_CW, Prescription.PLANT): PnvRotationAnchor(
        max_pnv_per_ac=158.0, optimal_rotation_yr=90
    ),
    (Ecoclass.CH_CW, Prescription.PLANT_CT): PnvRotationAnchor(
        max_pnv_per_ac=123.0, optimal_rotation_yr=100
    ),
    (Ecoclass.CH_CW, Prescription.PLANT_VM_PCT): PnvRotationAnchor(
        max_pnv_per_ac=331.0, optimal_rotation_yr=80
    ),
    (Ecoclass.CH_CW, Prescription.PLANT_VM_PCT_FERT): PnvRotationAnchor(
        max_pnv_per_ac=469.0, optimal_rotation_yr=70
    ),
    (Ecoclass.CH_CW, Prescription.PLANT_VM_PCT_CT): PnvRotationAnchor(
        max_pnv_per_ac=460.0, optimal_rotation_yr=90
    ),
    (Ecoclass.CH_CW, Prescription.PLANT_VM_PCT_FERT_CT): PnvRotationAnchor(
        max_pnv_per_ac=619.0, optimal_rotation_yr=80
    ),
    (Ecoclass.CD_CP, Prescription.NATURAL_REGEN): None,
    (Ecoclass.CD_CP, Prescription.PLANT): PnvRotationAnchor(
        max_pnv_per_ac=93.0, optimal_rotation_yr=90
    ),
    (Ecoclass.CD_CP, Prescription.PLANT_CT): PnvRotationAnchor(
        max_pnv_per_ac=58.0, optimal_rotation_yr=120
    ),
    (Ecoclass.CD_CP, Prescription.PLANT_VM_PCT): PnvRotationAnchor(
        max_pnv_per_ac=106.0, optimal_rotation_yr=90
    ),
    (Ecoclass.CD_CP, Prescription.PLANT_VM_PCT_FERT): PnvRotationAnchor(
        max_pnv_per_ac=110.0, optimal_rotation_yr=100
    ),
    (Ecoclass.CD_CP, Prescription.PLANT_VM_PCT_CT): PnvRotationAnchor(
        max_pnv_per_ac=203.0, optimal_rotation_yr=110
    ),
    (Ecoclass.CD_CP, Prescription.PLANT_VM_PCT_FERT_CT): PnvRotationAnchor(
        max_pnv_per_ac=229.0, optimal_rotation_yr=100
    ),
    (Ecoclass.CR_CF, Prescription.NATURAL_REGEN): PnvRotationAnchor(
        max_pnv_per_ac=65.0, optimal_rotation_yr=90
    ),
    (Ecoclass.CR_CF, Prescription.PLANT): PnvRotationAnchor(
        max_pnv_per_ac=80.0, optimal_rotation_yr=100
    ),
    (Ecoclass.CR_CF, Prescription.PLANT_CT): None,
    (Ecoclass.CR_CF, Prescription.PLANT_VM_PCT): PnvRotationAnchor(
        max_pnv_per_ac=44.0, optimal_rotation_yr=100
    ),
    (Ecoclass.CR_CF, Prescription.PLANT_VM_PCT_FERT): None,
    (Ecoclass.CR_CF, Prescription.PLANT_VM_PCT_CT): PnvRotationAnchor(
        max_pnv_per_ac=94.0, optimal_rotation_yr=120
    ),
    (Ecoclass.CR_CF, Prescription.PLANT_VM_PCT_FERT_CT): None,
    (Ecoclass.CM_CE, Prescription.NATURAL_REGEN): None,
    (Ecoclass.CM_CE, Prescription.PLANT): PnvRotationAnchor(
        max_pnv_per_ac=-4.0, optimal_rotation_yr=150
    ),
    (Ecoclass.CM_CE, Prescription.PLANT_CT): None,
    (Ecoclass.CM_CE, Prescription.PLANT_VM_PCT): PnvRotationAnchor(
        max_pnv_per_ac=-150.0, optimal_rotation_yr=150
    ),
    (Ecoclass.CM_CE, Prescription.PLANT_VM_PCT_FERT): None,
    (Ecoclass.CM_CE, Prescription.PLANT_VM_PCT_CT): PnvRotationAnchor(
        max_pnv_per_ac=-153.0, optimal_rotation_yr=150
    ),
    (Ecoclass.CM_CE, Prescription.PLANT_VM_PCT_FERT_CT): None,
}


class MatureTypePnv(BaseModel):
    """PNV ($/ac) for harvesting an existing mature (over-mature) vegetation
    type in period 1 or period 2. Table 5.4 (p.76)."""

    ecoclass: Ecoclass
    vegetation_type: str
    age_yr: int
    pnv_period1_per_ac: float
    pnv_period2_per_ac: float


#: Table 5.4 (p.76): PNV ($/ac) of the five mature vegetation types in
#: periods 1 and 2. CM-CE sawtimber is negatively-valued.
MATURE_TYPE_PNV: tuple[MatureTypePnv, ...] = (
    MatureTypePnv(
        ecoclass=Ecoclass.CH_CW,
        vegetation_type="sawtimber",
        age_yr=195,
        pnv_period1_per_ac=7646.0,
        pnv_period2_per_ac=6167.0,
    ),
    MatureTypePnv(
        ecoclass=Ecoclass.CH_CW,
        vegetation_type="two-storied",
        age_yr=115,
        pnv_period1_per_ac=3468.0,
        pnv_period2_per_ac=2970.0,
    ),
    MatureTypePnv(
        ecoclass=Ecoclass.CD_CP,
        vegetation_type="sawtimber",
        age_yr=125,
        pnv_period1_per_ac=3421.0,
        pnv_period2_per_ac=2813.0,
    ),
    MatureTypePnv(
        ecoclass=Ecoclass.CR_CF,
        vegetation_type="sawtimber",
        age_yr=225,
        pnv_period1_per_ac=6582.0,
        pnv_period2_per_ac=5579.0,
    ),
    MatureTypePnv(
        ecoclass=Ecoclass.CM_CE,
        vegetation_type="sawtimber",
        age_yr=175,
        pnv_period1_per_ac=-1042.0,
        pnv_period2_per_ac=-674.0,
    ),
)


class LandbaseSpec(BaseModel):
    """One of the 18 initial forest conditions (landbases). Table 5.5 (p.78).

    Each landbase covers 10,000 acres.
    """

    id: int = Field(ge=1, le=18)
    description: str


#: Table 5.5 (p.78): the 18 initial forest conditions, each 10,000 acres.
LANDBASE_ACRES = 10_000.0
LANDBASES: tuple[LandbaseSpec, ...] = (
    LandbaseSpec(id=1, description="All mature existing stands"),
    LandbaseSpec(id=2, description="All mature existing stands, ecoclass CM-CE excluded"),
    LandbaseSpec(id=3, description="Landbase 1 after 40 yr harvest, area control, 100-yr rotation"),
    LandbaseSpec(id=4, description="Landbase 2 after 40 yr harvest, area control, 100-yr rotation"),
    LandbaseSpec(id=5, description="Landbase 1 after 40 yr harvest, area control, 70-yr rotation"),
    LandbaseSpec(id=6, description="Landbase 2 after 40 yr harvest, area control, 70-yr rotation"),
    LandbaseSpec(id=7, description="Landbase 1 after 70 yr harvest, area control, 70-yr rotation"),
    LandbaseSpec(id=8, description="Landbase 2 after 70 yr harvest, area control, 70-yr rotation"),
    LandbaseSpec(id=9, description="Young-growth, intensive management, equal acres by age class"),
    LandbaseSpec(
        id=10, description="Young-growth, intensive management, unequal acres by age class"
    ),
    *[
        LandbaseSpec(id=i, description="Randomly generated young-growth forest")
        for i in range(11, 19)
    ],
)


__all__ = [
    "HORIZON_YEARS",
    "LANDBASES",
    "LANDBASE_ACRES",
    "MATURE_TYPE_PNV",
    "N_PERIODS",
    "PERIOD_LENGTH_YEARS",
    "PNV_ROTATION_ANCHORS",
    "PRICE_ESCALATION_RATE",
    "PRICE_ESCALATION_YEARS",
    "ROTATION_RANGES",
    "THESIS_DISCOUNT_RATE",
    "VOLUME_UNIT",
    "Ecoclass",
    "LandbaseSpec",
    "MatureTypePnv",
    "PnvRotationAnchor",
    "Prescription",
    "RotationRange",
]
