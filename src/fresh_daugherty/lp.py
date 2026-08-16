"""The open-loop harvest-scheduling LP (Phase 1, P1.2).

The Daugherty (1991) inner model: maximize present net value (4% discount,
delivered-log-price escalation +1%/yr for the first 50 years) over harvest
and regeneration decisions, subject to a harvest-flow (even-flow) constraint
and regeneration transitions. This is an open-loop formulation — the object
whose dynamic inconsistency the thesis (and this reproduction) studies.

Built on the ws3 Model I machinery (``model.add_problem``), so the LP
objective coefficient per prescription path is the discounted net cash flow.

The harvest-flow (even-flow) constraint supports two geometries:

- ``period1``: each period's harvest volume is tied to within
  ``flow_coefficient`` of period 1 (ws3's ``cflw_e`` reference-period band).
- ``consecutive``: each period's harvest volume is tied to within
  ``flow_coefficient`` of the *previous* period (the FORPLAN / thesis
  bounded-deviation-between-adjacent-periods form). This is implemented in
  fresh-daugherty (not via ws3 ``cflw_e``, which only anchors to a single
  reference period) by adding consecutive-period constraints directly to the
  compiled problem, so it works with the pinned PyPI ws3.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import ws3

from fresh_daugherty.instance.reconstruct import calibrated_params
from fresh_daugherty.instance.thesis import (
    PRICE_ESCALATION_RATE,
    PRICE_ESCALATION_YEARS,
    THESIS_DISCOUNT_RATE,
    HarvestFlowPolicy,
)
from fresh_daugherty.model import MATURE_RX, ecoclass_code


def _ecoclass_economics() -> dict[str, tuple[float, float]]:
    """Net delivered log price and harvest cost ($/MCF) per ecoclass code.

    Uses the real Umpqua FEIS economics (stumpage value net of logging, less
    the per-ecoclass access/road cost) — CM-CE is negatively valued. The
    calibrated reconstruction is the fallback if a real value is unavailable.
    """
    from fresh_daugherty.instance.feis import real_ecoclass_net_revenue
    from fresh_daugherty.instance.thesis import Ecoclass

    params = calibrated_params()
    econ: dict[str, tuple[float, float]] = {}
    for (eco, _rx), model in params.items():
        # ws3 lowercases theme values, so the model's dtk ecoclass is lowercase;
        # key the economics lookup by the lowercased code to match.
        code = ecoclass_code(eco).lower()
        if code in econ:
            continue
        try:
            net = real_ecoclass_net_revenue(Ecoclass(eco.value))
            # price = net + nominal harvest cost; net = price - hcost.
            econ[code] = (net + _NOMINAL_HARVEST_COST, _NOMINAL_HARVEST_COST)
        except (ValueError, KeyError):
            econ[code] = (
                model["econ"].net_price_per_mcf,
                model["econ"].harvest_cost_per_mcf,
            )
    return econ


#: Nominal harvest cost ($/MCF) folded out of the FEIS stumpage (which is
#: already net of logging/manufacturing); used only to keep the LP's
#: price-minus-cost structure explicit.
_NOMINAL_HARVEST_COST = 0.0


def _escalated(base: float, year: float) -> float:
    return base * (1.0 + PRICE_ESCALATION_RATE) ** min(year, PRICE_ESCALATION_YEARS)


def add_open_loop_problem(
    model: ws3.forest.ForestModel,
    *,
    flow_coefficient: float = 0.05,
    discount_rate: float = THESIS_DISCOUNT_RATE,
    price_escalation: bool = True,
    target_flow_mcf: float | None = None,
    flow_geometry: str = "period1",
    flow_decrease: float | None = None,
    flow_increase: float | None = None,
    terminal_constraints: bool = False,  # EXPERIMENTAL: see note in docstring
    name: str = "open-loop",
) -> object:
    """Add the open-loop NPV-max LP to ``model`` and return it.

    Harvest policy (the thesis's "harvest flow and ending period
    constraints"). With ``flow_geometry = "period1"`` an even-flow band ties
    each period's harvest volume to within ``flow_coefficient`` of period 1.
    With ``flow_geometry = "consecutive"`` (the thesis / FORPLAN "sequential
    flow" form, Table 5.6) each period's harvest is tied to the *previous*
    period: it may decrease by at most ``flow_decrease`` (default
    ``flow_coefficient``) and, if ``flow_increase`` is set, increase by at most
    ``flow_increase``. Set ``flow_decrease=0.0, flow_increase=None`` for
    non-declining yield (NDY). If ``target_flow_mcf`` is given, a target
    harvest-flow floor/ceiling is used instead (an AAC ceiling; overrides
    ``flow_geometry``).

    ``terminal_constraints`` (EXPERIMENTAL, default off): adds the thesis's
    ending-period inventory floor (ending growing stock >= 80% of the regulated
    forest's average inventory; thesis p.77). Known issue: the per-path
    ending-inventory coefficient does not yet match ws3's growing-stock
    accounting (regenerated-DT handling), so the floor can be infeasible. With
    the corrected (Table 5.4-faithful) case-study data the model does not
    exhibit the horizon-end liquidation these constraints guard against, so they
    are off by default; see `planning/thesis-formulation.md` and issue #42.
    """
    period_length = model.period_length
    econ = _ecoclass_economics()

    def _net_price(dtk, year: float) -> float:
        price, hcost = econ.get(str(dtk[1]).lower(), (0.0, 0.0))
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

    def coeff_c_inventory(fm: ws3.forest.ForestModel, path) -> dict[int, float]:
        """Standing (growing-stock) volume per ac along the path, per period.

        Uses the model's compiled yield curves at each node's age, so it is
        consistent with ws3's inventory accounting (flat past culmination).
        """
        out: dict[int, float] = {}
        for t, n in enumerate(path, start=1):
            d = n.data()
            out[t] = _standing_volume_per_ac(fm, d["dtk"], float(d["age"]))
        return out

    if flow_geometry not in ("period1", "consecutive", "none"):
        raise ValueError(
            f"flow_geometry must be 'period1', 'consecutive', or 'none', got {flow_geometry!r}"
        )

    # The thesis's ending-period (terminal) inventory constraint (p.77): ending
    # growing stock >= 80% of the regulated forest's average inventory. Used
    # with all harvest-flow-constrained runs to minimize horizon effects
    # (prevent horizon-end liquidation of the growing stock).
    use_terminal_inv = terminal_constraints and target_flow_mcf is None and flow_geometry != "none"

    coeff_funcs = {"z": coeff_c_z, "cflw_hv": coeff_c_hv}
    if use_terminal_inv:
        coeff_funcs["inventory"] = coeff_c_inventory
    cflw_e = None
    cgen_data = None
    if target_flow_mcf is not None:
        # Target harvest flow (an AAC ceiling): harvest <= target each period.
        # lb=0 so a young forest is not forced to harvest before stands reach
        # rotation age; the ceiling caps the rate once they do.
        cgen_data = {
            "cflw_hv": {
                "lb": dict.fromkeys(model.periods, 0.0),
                "ub": dict.fromkeys(model.periods, target_flow_mcf),
            }
        }
    elif flow_geometry == "none":
        # No harvest-flow constraint (the thesis's NHF policy, Table 5.6).
        cflw_e = None
    elif flow_geometry == "period1":
        cflw_e = {"cflw_hv": (dict.fromkeys(model.periods, flow_coefficient), 1)}
    else:  # consecutive (thesis "sequential flow", Table 5.6)
        # H_{n+1} >= (1 - flow_decrease) H_n  and, if flow_increase is set,
        # H_{n+1} <= (1 + flow_increase) H_n. flow_decrease=0.0 gives NDY.
        dec = flow_coefficient if flow_decrease is None else flow_decrease
        spec: dict[str, object] = {
            "decrease": dict.fromkeys(model.periods, dec),
            "ref": "consecutive",
        }
        if flow_increase is not None:
            spec["increase"] = dict.fromkeys(model.periods, flow_increase)
        cflw_e = {"cflw_hv": spec}

    if use_terminal_inv:
        # Ending-inventory floor (thesis p.77): ending growing stock >= 80% of
        # the regulated forest's average inventory. Target = 0.8 * sum over
        # ecoclasses of (landbase ecoclass area * avg inventory per ac).
        targets = _terminal_targets()
        eco_area: dict[str, float] = {}
        for dtk, dt in model.dtypes.items():
            eco = str(dtk[1]).lower()
            eco_area[eco] = eco_area.get(eco, 0.0) + float(sum(dt._areas[1].values()))
        inv_target = 0.8 * sum(
            eco_area.get(eco, 0.0) * avg_inv for eco, (avg_inv, _l) in targets.items()
        )
        final_period = list(model.periods)[-1]
        if inv_target > 0:
            cgen_data = cgen_data or {}
            cgen_data["inventory"] = {"lb": {final_period: inv_target}}

    problem = model.add_problem(
        name=name,
        coeff_funcs=coeff_funcs,
        cflw_e=cflw_e,
        cgen_data=cgen_data,
        acodes=("null", "harvest"),
        sense=ws3.opt.SENSE_MAXIMIZE,
        mask=tuple(["?"] * model.nthemes()),
        workers=1,
        verbose=False,
    )
    return problem


def _terminal_targets() -> dict[str, tuple[float, float]]:
    """Per-ecoclass (average inventory, LTSY) per acre for the regenerated forest.

    The thesis's ending-period constraints (p.77) tie the terminal state to the
    forest regulated under the selected regenerated prescriptions, at the
    highest-PNV rotation. Harvest regenerates to the base (PLANT) prescription.
    Returns {ecoclass_code: (avg_inventory_mcf_ac, ltsy_mcf_ac_period)} where
    LTSY (long-term sustained yield) per period = standing volume at the
    optimal rotation / rotation * period_length.
    """
    import numpy as np

    from fresh_daugherty.instance.feis import real_yield_curve
    from fresh_daugherty.instance.thesis import (
        PERIOD_LENGTH_YEARS,
        PNV_ROTATION_ANCHORS,
        Ecoclass,
        Prescription,
    )

    out: dict[str, tuple[float, float]] = {}
    for eco in Ecoclass:
        anchor = PNV_ROTATION_ANCHORS.get((eco, Prescription.PLANT))
        if anchor is None:
            continue
        r = anchor.optimal_rotation_yr
        curve = real_yield_curve(eco, Prescription.PLANT, max_age=r)
        v_r = curve.get(r, 0.0)
        avg_inv = float(np.mean([curve.get(int(a), 0.0) for a in range(0, r + 1, 10)]))
        ltsy = (v_r / r) * PERIOD_LENGTH_YEARS  # MCF/ac per period, harvestable in perpetuity
        out[ecoclass_code(eco).lower()] = (avg_inv, ltsy)
    return out


def _standing_volume_per_ac(model: ws3.forest.ForestModel, dtk, age: float) -> float:
    """Standing volume (MCF/ac) of a development type at a given age.

    Mature/existing DTs are in ``model.dtypes``; regenerated (managed) DTs are
    created by transitions during the solve and are evaluated from the FEIS
    yield curve. Flat past culmination, so safe for over-mature ages.
    """
    rx, origin = str(dtk[2]), str(dtk[3])
    if rx == MATURE_RX or origin == "existing":
        dt = model.dtypes.get(dtk)
        if dt is None:
            return 0.0
        curve = dt.ycomp("totvol")
        return float(curve.interp(min(age, model.max_age))) if curve is not None else 0.0
    # Regenerated / managed DT: FEIS standing-volume curve at the age.
    from fresh_daugherty.instance.feis import real_yield_curve
    from fresh_daugherty.instance.thesis import Ecoclass, Prescription

    eco = next(e for e in Ecoclass if ecoclass_code(e).lower() == str(dtk[1]).lower())
    curve = real_yield_curve(eco, Prescription(int(rx[2:])), max_age=int(max(age, 300)))
    ages = sorted(curve)
    if not ages:
        return 0.0
    age_c = min(max(age, ages[0]), ages[-1])
    return float(np.interp(age_c, ages, [curve[a] for a in ages]))


def flow_kwargs_for_policy(policy: HarvestFlowPolicy) -> dict:
    """Map a thesis harvest-flow policy (Table 5.6) to ``add_open_loop_problem`` kwargs.

    NHF (no decrease/increase) -> no flow constraint; the sequential-flow sets
    (NDY, -10%, -20%, +/-10%, +/-20%) -> the consecutive-period geometry with
    the policy's max-decrease and (optional) max-increase tolerances.
    """
    if policy.max_decrease is None and policy.max_increase is None:
        return {"flow_geometry": "none"}
    return {
        "flow_geometry": "consecutive",
        "flow_decrease": policy.max_decrease,
        "flow_increase": policy.max_increase,
    }


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
