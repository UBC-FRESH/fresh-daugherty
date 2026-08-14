"""The open-loop harvest-scheduling LP (Phase 1, P1.2).

The Daugherty (1991) inner model: maximize present net value (4% discount,
delivered-log-price escalation +1%/yr for the first 50 years) over harvest
and regeneration decisions, subject to a harvest-flow (even-flow) constraint
and regeneration transitions. This is an open-loop formulation — the object
whose dynamic inconsistency the thesis (and this reproduction) studies.

Built on the ws3 Model I machinery (``model.add_problem``), so the LP
objective coefficient per prescription path is the discounted net cash flow
and the even-flow band ties each period's harvest volume to period 1.
"""

from __future__ import annotations

import pandas as pd
import ws3

from fresh_daugherty.instance.reconstruct import calibrated_params
from fresh_daugherty.instance.thesis import (
    PRICE_ESCALATION_RATE,
    PRICE_ESCALATION_YEARS,
    THESIS_DISCOUNT_RATE,
)
from fresh_daugherty.model import ecoclass_code


def _ecoclass_economics() -> dict[str, tuple[float, float]]:
    """Net delivered log price and harvest cost ($/MCF) per ecoclass code."""
    params = calibrated_params()
    econ: dict[str, tuple[float, float]] = {}
    for (eco, _rx), model in params.items():
        econ[ecoclass_code(eco)] = (
            model["econ"].net_price_per_mcf,
            model["econ"].harvest_cost_per_mcf,
        )
    return econ


def _escalated(base: float, year: float) -> float:
    return base * (1.0 + PRICE_ESCALATION_RATE) ** min(year, PRICE_ESCALATION_YEARS)


def add_open_loop_problem(
    model: ws3.forest.ForestModel,
    *,
    flow_coefficient: float = 0.05,
    discount_rate: float = THESIS_DISCOUNT_RATE,
    price_escalation: bool = True,
    name: str = "open-loop",
) -> object:
    """Add the open-loop NPV-max even-flow LP to ``model`` and return it."""
    period_length = model.period_length
    econ = _ecoclass_economics()

    def _net_price(dtk, year: float) -> float:
        price, hcost = econ.get(dtk[1], (0.0, 0.0))
        p = _escalated(price, year) if price_escalation else price
        return p - hcost

    def coeff_c_z(fm: ws3.forest.ForestModel, path) -> float:
        result = 0.0
        for t, n in enumerate(path, start=1):
            d = n.data()
            if fm.is_harvest(d["acode"]):
                vol = fm.compile_product(t, "totvol", d["acode"], [d["dtk"]], d["age"], coeff=False)
                net = _net_price(d["dtk"], t * period_length)
                result += (1.0 + discount_rate) ** (-t * period_length) * (net * vol)
        return result

    def coeff_c_hv(fm: ws3.forest.ForestModel, path) -> dict[int, float]:
        out: dict[int, float] = {}
        for t, n in enumerate(path, start=1):
            d = n.data()
            if d["acode"] == "harvest":
                vol = fm.compile_product(t, "totvol", d["acode"], [d["dtk"]], d["age"], coeff=False)
                if vol:
                    out[t] = vol
        return out

    coeff_funcs = {"z": coeff_c_z, "cflw_hv": coeff_c_hv}
    cflw_e = {"cflw_hv": (dict.fromkeys(model.periods, flow_coefficient), 1)}
    return model.add_problem(
        name=name,
        coeff_funcs=coeff_funcs,
        cflw_e=cflw_e,
        cgen_data=None,
        acodes=("null", "harvest"),
        sense=ws3.opt.SENSE_MAXIMIZE,
        mask=tuple(["?"] * model.nthemes()),
        workers=1,
        verbose=False,
    )


def solve_open_loop(model: ws3.forest.ForestModel, problem: object) -> pd.DataFrame:
    """Solve the LP, compile and apply the schedule, return per-period results."""
    problem.solve(verbose=False)
    schedule = model.compile_schedule(problem)
    model.reset()
    model.apply_schedule(
        schedule,
        force_integral_area=False,
        override_operability=False,
        fuzzy_age=False,
        recourse_enabled=False,
        verbose=False,
        compile_c_ycomps=True,
    )
    return pd.DataFrame(
        {
            "period": model.periods,
            "harvest_area_ac": [
                model.compile_product(p, "1.", acode="harvest") for p in model.periods
            ],
            "harvest_volume_mcf": [
                model.compile_product(p, "totvol", acode="harvest") for p in model.periods
            ],
            "growing_stock_mcf": [model.inventory(p, "totvol") for p in model.periods],
        }
    )


__all__ = ["add_open_loop_problem", "solve_open_loop"]
