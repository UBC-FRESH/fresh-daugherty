"""Build the Daugherty (1991) case-study forest as a ws3 model (Phase 1, P1.2).

Reconstructs the Umpqua case-study as a ws3 ``ForestModel`` (Model I):
development types are the managed young-growth (ecoclass x prescription) and
the existing mature (over-mature) vegetation types; the harvest action is
operable over the thesis rotation window (Table 5.2); harvest regenerates the
stand to age 0 of the same (ecoclass, prescription). Yield curves come from
the calibrated reconstruction (:mod:`fresh_daugherty.instance.reconstruct`);
mature-type volumes are recovered from the Table 5.4 PNV anchors.

Theme structure (5 themes): FOREST, ECOCLASS, RX, ORIGIN, STATE.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import ws3.forest

from fresh_daugherty.instance.reconstruct import calibrated_params, yield_volume
from fresh_daugherty.instance.thesis import (
    MATURE_TYPE_PNV,
    PERIOD_LENGTH_YEARS,
    ROTATION_RANGES,
    Ecoclass,
    Prescription,
)

THEME_COUNT = 5
BASE_YEAR = 1987  # the thesis data source vintage (USDA 1987 Umpqua model)
FOREST = "umpqua"

#: Mature (existing over-mature) vegetation types are modelled as
#: prescription "mature" DTs at their Table 5.4 ages.
MATURE_RX = "mature"


def ecoclass_code(eco: Ecoclass) -> str:
    """Single-token ecoclass code for the ws3 theme (no hyphen)."""
    return eco.value.replace("-", "")


def _dtk(eco: Ecoclass, rx: str, origin: str) -> tuple[str, str, str, str, str]:
    return (FOREST, ecoclass_code(eco), rx, origin, "baseline")


def _yield_points(yp, max_age: int) -> list[tuple[int, float]]:
    return [
        (age, round(float(yield_volume(age, yp)), 6))
        for age in range(0, max_age + 1, PERIOD_LENGTH_YEARS)
    ]


def mature_volume_mcf(mt, net_price_per_mcf: float) -> float:
    """Recover the mature stand volume (MCF/ac) from its Table 5.4 PNV anchor.

    Period-1 PNV is essentially the undiscounted single-harvest net revenue of
    the existing stand, so ``V ~ PNV_period1 / net_price_per_mcf``.
    """
    return float(mt.pnv_period1_per_ac / net_price_per_mcf)


def _mature_yield_points(net_volume: float, age_yr: int, max_age: int) -> list[tuple[int, float]]:
    """A mature (over-mature) stand's yield curve: flat at its recovered volume.

    Over-mature stands have roughly constant (culminated) volume over the
    horizon; the economically relevant fact (declining PNV) comes from the
    economics, not the volume curve.
    """
    return [(age, round(net_volume, 6)) for age in range(0, max_age + 1, PERIOD_LENGTH_YEARS)]


def build_woodstock_sections(
    out_dir: str | Path,
    *,
    areas: pd.DataFrame,
    max_age: int = 220,
    model_name: str = "daugherty",
) -> list[Path]:
    """Write the five Woodstock-format sections for the case-study model."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    params = calibrated_params()

    # Net price per ecoclass for mature-volume recovery.
    net_price = {}
    for eco in Ecoclass:
        cell = next((m for (e, _rx), m in params.items() if e is eco), None)
        if cell is not None:
            net_price[eco] = cell["econ"].net_price_per_mcf - cell["econ"].harvest_cost_per_mcf

    # --- landscape / themes ---
    ecoclasses = sorted({ecoclass_code(e) for e in Ecoclass})
    rx_codes = sorted({f"rx{int(rx)}" for rx in Prescription} | {MATURE_RX})
    (out / f"{model_name}.lan").write_text(
        "*THEME FOREST\numpqua\n\n"
        "*THEME ECOCLASS\n" + "".join(f"{c}\n" for c in ecoclasses) + "\n"
        "*THEME RX\n" + "".join(f"{c}\n" for c in rx_codes) + "\n"
        "*THEME ORIGIN\nexisting\nregenerated\n\n"
        "*THEME STATE\nbaseline\n"
    )

    # --- areas ---
    with open(out / f"{model_name}.are", "w") as f:
        for row in areas.itertuples():
            if float(row.area_ac) <= 0:
                continue
            f.write(
                f"*A {row.forest} {row.ecoclass} {row.rx} {row.origin} "
                f"{row.state} {int(row.age)} {float(row.area_ac):.6f}\n"
            )

    # --- yields ---
    with open(out / f"{model_name}.yld", "w") as f:
        # Managed young-growth DTs.
        for (eco, rx), model in params.items():
            dtk = _dtk(eco, f"rx{int(rx)}", "regenerated")
            f.write(f"*Y ? {dtk[1]} {dtk[2]} {dtk[3]} {dtk[4]}\n_AGE totvol\n")
            for age, vol in _yield_points(model["yield"], max_age):
                f.write(f"{age} {vol:.6f}\n")
            f.write("\n")
        # Mature DTs (existing, over-mature).
        for mt in MATURE_TYPE_PNV:
            dtk = _dtk(mt.ecoclass, MATURE_RX, "existing")
            vol = mature_volume_mcf(mt, net_price[mt.ecoclass])
            f.write(f"*Y ? {dtk[1]} {dtk[2]} {dtk[3]} {dtk[4]}\n_AGE totvol\n")
            for age, v in _mature_yield_points(vol, mt.age_yr, max_age):
                f.write(f"{age} {v:.6f}\n")
            f.write("\n")

    # --- actions --- (harvest operable in the per-DT rotation window)
    with open(out / f"{model_name}.act", "w") as f:
        f.write("*ACTION harvest Y\n")
        # One OPERABLE block per (ecoclass, rx) managed DT rotation window.
        for (eco, rx), _m in params.items():
            rng = ROTATION_RANGES[(eco, rx)]
            assert rng is not None
            f.write(
                f"*OPERABLE harvest\n"
                f"? {ecoclass_code(eco)} rx{int(rx)} regenerated baseline "
                f"_AGE >= {rng.lo} and _AGE <= {rng.hi}\n"
            )
        # Mature types are immediately harvestable (over-mature).
        for mt in MATURE_TYPE_PNV:
            f.write(
                f"*OPERABLE harvest\n"
                f"? {ecoclass_code(mt.ecoclass)} {MATURE_RX} existing baseline _AGE >= 0\n"
            )

    # --- transitions ---
    # Harvest regenerates the stand to age 0. Mature (existing) stands convert
    # to the ecoclass's base managed prescription (rx2 = plant); managed stands
    # regenerate to themselves. (The full regenerated-prescription choice is a
    # documented refinement; the base prescription is the default target.)
    with open(out / f"{model_name}.trn", "w") as f:
        f.write(
            # Mature (existing) -> base managed (regenerated rx2), age 0.
            "*CASE harvest\n"
            "*SOURCE ? ? mature existing baseline\n"
            "*TARGET ? ? rx2 regenerated baseline 100 _AGE 0\n"
            # Managed (regenerated) -> itself, age 0.
            "*CASE harvest\n"
            "*SOURCE ? ? ? regenerated baseline\n"
            "*TARGET ? ? ? regenerated baseline 100 _AGE 0\n"
        )

    return [out / f"{model_name}.{s}" for s in ("lan", "are", "yld", "act", "trn")]


def bootstrap_model(
    model_path: str | Path, *, horizon: int, model_name: str = "daugherty"
) -> ws3.forest.ForestModel:
    """Load the Woodstock sections into a ws3 ``ForestModel``."""
    model = ws3.forest.ForestModel(
        model_name=model_name,
        model_path=str(model_path),
        base_year=BASE_YEAR,
        horizon=horizon,
        period_length=PERIOD_LENGTH_YEARS,
        max_age=300,
    )
    model.import_landscape_section()
    model.import_areas_section()
    model.import_yields_section()
    model.import_actions_section()
    model.import_transitions_section()
    model.compile_actions()
    model.reset()
    if model.nthemes() != THEME_COUNT:
        raise ValueError(f"expected {THEME_COUNT} themes, got {model.nthemes()}")
    return model


def prepare_optimization(model: ws3.forest.ForestModel, *, horizon: int) -> ws3.forest.ForestModel:
    """Add the null action with horizon-long operability (stands age through)."""
    null_max_age = 300 + horizon * PERIOD_LENGTH_YEARS
    null_oe = f"_age >= 0 and _age <= {null_max_age}"
    wildcard = tuple(["?"] * model.nthemes())
    model.add_null_action()
    model.oper_expr["null"] = {wildcard: null_oe}
    for dt in model.dtypes.values():
        dt._max_age = null_max_age
        dt.oper_expr["null"] = [null_oe]
        dt.operability.pop("null", None)
    model.reset_actions()
    model.actions["harvest"].is_harvest = True
    return model


__all__ = [
    "BASE_YEAR",
    "FOREST",
    "MATURE_RX",
    "THEME_COUNT",
    "bootstrap_model",
    "build_woodstock_sections",
    "ecoclass_code",
    "mature_volume_mcf",
    "prepare_optimization",
]
