"""Case-study instance for the Daugherty (1991) reproduction (Phase 1).

- :mod:`fresh_daugherty.instance.thesis` — the transcribed thesis reference
  data (Tables 5.1-5.5, horizon, objective), the anchors the reconstruction
  is calibrated against.
- :mod:`fresh_daugherty.instance.reconstruct` — the documented reconstruction
  of the per-age yield curves and price/cost model (the raw tables are in the
  archival USDA 1987 Umpqua EIS, not the thesis), calibrated to the thesis
  anchors.
"""

from .feis import (
    SITE_INDEX_BY_ECOCLASS,
    SPECIES_ECONOMICS,
    UMPQUA_YIELD_TABLES,
    standing_volume_curve,
    yield_tables_for,
)
from .thesis import (
    CMAI_CULMINATION_AGE_YR,
    HORIZON_YEARS,
    LANDBASE_ACRES,
    LANDBASES,
    MATURE_TYPE_PNV,
    N_PERIODS,
    PERIOD_LENGTH_YEARS,
    PNV_ROTATION_ANCHORS,
    PRICE_ESCALATION_RATE,
    PRICE_ESCALATION_YEARS,
    ROTATION_RANGES,
    THESIS_DISCOUNT_RATE,
    VOLUME_UNIT,
    Ecoclass,
    LandbaseSpec,
    MatureTypePnv,
    PnvRotationAnchor,
    Prescription,
    RotationRange,
)

__all__ = [
    "CMAI_CULMINATION_AGE_YR",
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
    "SITE_INDEX_BY_ECOCLASS",
    "SPECIES_ECONOMICS",
    "THESIS_DISCOUNT_RATE",
    "UMPQUA_YIELD_TABLES",
    "VOLUME_UNIT",
    "Ecoclass",
    "LandbaseSpec",
    "MatureTypePnv",
    "PnvRotationAnchor",
    "Prescription",
    "RotationRange",
    "standing_volume_curve",
    "yield_tables_for",
]
