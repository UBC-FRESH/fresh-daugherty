"""The open-loop harvest-scheduling LP (Phase 1, P1.2).

The Daugherty (1991) inner model: maximize present net value (4% discount,
delivered-log-price escalation +1%/yr for the first 50 years) over harvest
and regeneration decisions, subject to a harvest-flow (even-flow) constraint
and regeneration transitions. This is an open-loop formulation — the object
whose dynamic inconsistency the thesis (and this reproduction) studies.

Built on the ws3 Model I machinery (``model.add_problem``), so the LP
objective coefficient per prescription path is the discounted net cash flow.

The harvest-flow (even-flow) constraint supports these geometries:

- ``period1``: each period's harvest volume is tied to within
  ``flow_coefficient`` of period 1 (ws3's ``cflw_e`` reference-period band).
- ``consecutive``: each period's harvest volume is tied to within
  ``flow_coefficient`` of the *previous* period (the FORPLAN / thesis
  bounded-deviation-between-adjacent-periods form), via ws3 v1.1.0a5's
  consecutive-reference ``cflw_e`` spec (contributed upstream from this
  project; UBC-FRESH/ws3#152).
- ``rolling_mean``: each period's flow is floored at the mean of the previous
  ``flow_window`` periods (E4, P12), added post-compile by
  ``_add_rolling_mean_flow``.

All flow geometries can be denominated in volume (``cflw_hv``, the thesis's
form) or undiscounted net revenue (``cflw_rv``, E3 / P11) via
``flow_denominator``.
"""

from __future__ import annotations

import itertools

import pandas as pd
import ws3

from fresh_daugherty.instance.discount import DiscountPath, constant_path
from fresh_daugherty.instance.reconstruct import calibrated_params
from fresh_daugherty.instance.thesis import (
    PRICE_ESCALATION_RATE,
    PRICE_ESCALATION_YEARS,
    THESIS_DISCOUNT_RATE,
    HarvestFlowPolicy,
)
from fresh_daugherty.model import ecoclass_code

#: Relative slack on bounds built from *realized* harvests (the carried flow
#: anchor and the realized-history rolling-mean floor). Realized volumes carry
#: float noise of ~1e-9--1e-6 relative; an exact bound at the realized level can
#: then be infeasible by that noise, which triggered the anchor/floor relaxation
#: fallback and silently switched the replanning institution (P15.1, #83). Six
#: orders of magnitude below any policy tolerance.
HISTORY_RTOL = 1e-6


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


def _tighten_period_harvest(
    cgen_data: dict | None,
    *,
    period: int,
    lb: float | None = None,
    ub: float | None = None,
) -> dict:
    """Intersect harvest-volume bounds for ``period`` with any already present
    (an empty intersection makes the problem infeasible)."""
    cgen_data = cgen_data or {}
    hv = cgen_data.setdefault("cflw_hv", {})
    lbs = hv.setdefault("lb", {})
    ubs = hv.setdefault("ub", {})
    if lb is not None:
        lbs[period] = max(lbs.get(period, lb), lb)
    if ub is not None:
        ubs[period] = min(ubs.get(period, ub), ub)
    return cgen_data


def _tighten_period1_harvest(
    cgen_data: dict | None, *, lb: float | None = None, ub: float | None = None
) -> dict:
    """Intersect period-1 harvest-volume bounds with any already present.

    Every caller that bounds the period-1 harvest (cap, carried anchor,
    tail-fixed band) goes through here, so the result is the intersection of
    all requested bounds regardless of order. An empty intersection (lb > ub)
    is kept and makes the problem infeasible, which is the correct reading.
    """
    return _tighten_period_harvest(cgen_data, period=1, lb=lb, ub=ub)


def regulated_forest_targets(model: ws3.forest.ForestModel) -> dict[str, float]:
    """Average inventory and long-term sustained yield of the forest regulated
    under each stratum's regeneration prescription (thesis p. 77).

    Each stratum's area (at the subproblem's first period) regenerates under a
    fixed prescription: mature (existing) stands under planting (rx2), managed
    stands under their own prescription. For each (ecoclass, prescription) the
    rotation is the Table 5.3 highest-PNV rotation R; the average inventory per
    acre is the mean standing volume over a rotation (trapezoid over ages 0..R
    on the period grid) and the sustained yield per acre per period is
    V(R) / R x period length, from the model's own yield curves. Returns total
    ``avg_inventory_mcf`` and ``ltsy_mcf_per_period``.
    """
    from fresh_daugherty.instance.reconstruct import calibrated_params
    from fresh_daugherty.instance.thesis import (
        PNV_ROTATION_ANCHORS,
        Ecoclass,
        Prescription,
    )
    from fresh_daugherty.model import MAX_AGE, _yield_points_for

    params = calibrated_params()
    by_code = {ecoclass_code(e).lower(): e for e in Ecoclass}
    # Read the subproblem's initial areas: building or applying a previous
    # problem leaves the model's period-1 areas changed, and the targets
    # (right-hand sides) must not depend on what was built before (P18.2
    # follow-up: the free and tail-fixed problems of one replan got different
    # targets). ws3 resets the same way before building trees.
    model.reset()
    area: dict[tuple[Ecoclass, Prescription], float] = {}
    for dtk, dt in model.dtypes.items():
        a = float(sum(dt._areas[1].values()))
        if a <= 0:
            continue
        eco = by_code[str(dtk[1]).lower()]
        rx = Prescription.PLANT if str(dtk[3]) == "existing" else Prescription(int(str(dtk[2])[2:]))
        area[(eco, rx)] = area.get((eco, rx), 0.0) + a
    inv = ltsy = 0.0
    step = model.period_length
    for (eco, rx), a in area.items():
        r = PNV_ROTATION_ANCHORS[(eco, rx)].optimal_rotation_yr
        curve = dict(_yield_points_for(eco, rx, params[(eco, rx)], MAX_AGE))
        vols = [curve[age] for age in range(0, r + 1, step)]
        avg = sum((v0 + v1) / 2 for v0, v1 in itertools.pairwise(vols)) / (len(vols) - 1)
        inv += a * avg
        ltsy += a * curve[r] / r * step
    return {"avg_inventory_mcf": inv, "ltsy_mcf_per_period": ltsy}


def add_open_loop_problem(
    model: ws3.forest.ForestModel,
    *,
    flow_coefficient: float = 0.05,
    discount_rate: float = THESIS_DISCOUNT_RATE,
    discount_path: DiscountPath | None = None,
    flow_denominator: str = "volume",
    price_escalation: bool = True,
    target_flow_mcf: float | None = None,
    flow_geometry: str = "period1",
    flow_decrease: float | None = None,
    flow_increase: float | None = None,
    terminal_constraints: bool = True,
    abs_period: int = 1,
    fix_period1_harvest_mcf: float | None = None,
    prev_harvest_mcf: float | None = None,
    flow_window: int = 2,
    realized_history: tuple[float, ...] | None = None,
    history_rtol: float = HISTORY_RTOL,
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
    ``flow_geometry``). The ``target_flow_mcf`` ceiling is also the E2 (P10)
    **max-harvest-cap** form used by the even-flow cap search
    (``evenflow.calibrate_even_flow_cap``): a per-period cap with a zero lower
    bound, so the cap-only problem is always feasible.

    ``flow_denominator`` (E3, P11): ``"volume"`` (default; the thesis's form,
    the flow rows carry harvest volume in MCF) or ``"revenue"`` (the flow rows
    carry *undiscounted* net revenue in $, at absolute-calendar-year escalated
    prices). The bounded-deviation policies (NDY, sequential flow) then link
    consecutive periods' revenue instead of volume. Mechanically this is a
    coefficient change in the flow rows only (revenue = volume x net price);
    the objective and all volume-keyed general constraints (the E2 cap, the
    gap diagnostic's period-1 fix) are unchanged.

    ``discount_path`` (E1, P9): a per-period discount-rate path. When given, it
    overrides ``discount_rate``; the scalar entry point is kept as a wrapper
    that builds the equivalent ``constant`` path, and a constant path produces
    objective coefficients bit-identical to the pre-E1 scalar convention (see
    ``instance/discount.py``). The path is indexed by the subproblem's
    *relative* period (each replanning planner applies the path from her own
    present; discounting stays relative while price escalation is absolute).

    ``terminal_constraints`` (default on; thesis p. 77): with every
    flow-constrained policy (not NHF, not the E2 cap; thesis p. 80) the final
    period carries (i) an ending-inventory floor, standing volume >= 80% of the
    average inventory of the forest regulated under each stratum's regeneration
    prescription, and (ii) a final-harvest cap, harvest <= 120% of that
    forest's long-term sustained yield, both at the Table 5.3 highest-PNV
    rotation (``regulated_forest_targets``). The inventory coefficient is ws3's
    own inventory of each column's post-action state (P18.2, #112; an earlier
    hand-rolled coefficient used per-acre units and the pre-action state).
    """
    period_length = model.period_length
    path = discount_path if discount_path is not None else constant_path(discount_rate)
    discount_factors = path.factors(horizon=len(list(model.periods)), period_length=period_length)
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
                # Price escalation is an ABSOLUTE-calendar-time phenomenon: the
                # replanning subproblem's relative period t is absolute year
                # (abs_period - 1 + t) * period_length. (Discounting stays
                # relative to the subproblem's present, per the Bellman tail.)
                net = _net_price(d["dtk"], (abs_period - 1 + t) * period_length)
                result += discount_factors[t - 1] * (net * vol)
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

    def coeff_c_rv(fm: ws3.forest.ForestModel, path) -> dict[int, float]:
        """Undiscounted net revenue per period along the path (E3 flow rows)."""
        out: dict[int, float] = {}
        for t, n in enumerate(path, start=1):
            d = n.data()
            if d["acode"] == "harvest":
                vol = fm.compile_product(t, "totvol", d["acode"], [d["dtk"]], d["age"], coeff=False)
                if vol:
                    net = _net_price(d["dtk"], (abs_period - 1 + t) * period_length)
                    out[t] = net * vol
        return out

    def coeff_c_inventory(fm: ws3.forest.ForestModel, path) -> dict[int, float]:
        """Standing volume at the end of each period along the path, in total
        units (the column's stratum area x yield), from ws3's own inventory of
        the post-action state. ``ForestModel.inventory`` ages areas by one
        period before matching ``age``, so the filter is ``_age`` plus one
        period (verified against the inventory of an applied schedule)."""
        out: dict[int, float] = {}
        for t, n in enumerate(path, start=1):
            d = n.data()
            out[t] = fm.inventory(
                t, yname="totvol", age=d["_age"] + fm.period_length, dtype_keys=[d["_dtk"]]
            )
        return out

    if flow_geometry not in ("period1", "consecutive", "none", "rolling_mean"):
        raise ValueError(
            "flow_geometry must be 'period1', 'consecutive', 'none', or 'rolling_mean', "
            f"got {flow_geometry!r}"
        )
    if flow_window < 1:
        raise ValueError(f"flow_window must be >= 1, got {flow_window}")
    if flow_denominator not in ("volume", "revenue"):
        raise ValueError(
            f"flow_denominator must be 'volume' or 'revenue', got {flow_denominator!r}"
        )
    # The flow rows are denominated in volume (cflw_hv, the thesis's form) or
    # undiscounted net revenue (cflw_rv, E3). Volume-keyed general constraints
    # (E2 cap, gap-diagnostic period-1 fix) always stay on volume.
    flow_key = "cflw_hv" if flow_denominator == "volume" else "cflw_rv"

    # The thesis's terminal constraints (p. 77), with every harvest-flow policy
    # but not NHF (p. 80), nor the E2 cap (which replaces the flow constraint).
    use_terminal_inv = terminal_constraints and target_flow_mcf is None and flow_geometry != "none"

    coeff_funcs = {"z": coeff_c_z, "cflw_hv": coeff_c_hv, "cflw_rv": coeff_c_rv}
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
        cflw_e = {flow_key: (dict.fromkeys(model.periods, flow_coefficient), 1)}
    elif flow_geometry == "rolling_mean":
        # E4 (P12): backwards-facing rolling-mean NDY rows, added post-compile
        # by _add_rolling_mean_flow below (ws3's cflw_e cannot express
        # multi-period windows).
        cflw_e = None
    else:  # consecutive (thesis "sequential flow", Table 5.6)
        # H_{n+1} >= (1 - flow_decrease) H_n  and, if flow_increase is set,
        # H_{n+1} <= (1 + flow_increase) H_n. flow_decrease=0.0 gives NDY.
        # Under flow_denominator="revenue" these link net revenue R_n (E3).
        dec = flow_coefficient if flow_decrease is None else flow_decrease
        spec: dict[str, object] = {
            "decrease": dict.fromkeys(model.periods, dec),
            "ref": "consecutive",
        }
        if flow_increase is not None:
            spec["increase"] = dict.fromkeys(model.periods, flow_increase)
        cflw_e = {flow_key: spec}

    if use_terminal_inv:
        targets = regulated_forest_targets(model)
        final_period = list(model.periods)[-1]
        cgen_data = cgen_data or {}
        cgen_data["inventory"] = {"lb": {final_period: 0.8 * targets["avg_inventory_mcf"]}}
        cgen_data = _tighten_period_harvest(
            cgen_data, period=final_period, ub=1.2 * targets["ltsy_mcf_per_period"]
        )

    if prev_harvest_mcf is not None and flow_geometry == "consecutive":
        if flow_denominator != "volume":
            # The carried anchor bounds period-1 *volume*; a revenue-denominated
            # policy would need a revenue anchor. Refuse rather than silently
            # anchor the wrong quantity (P16.1, #92).
            raise ValueError("carried flow history is implemented for volume-denominated flow only")
        # Carry the harvest-flow history: the subproblem's first-period harvest
        # is anchored to the realized previous period's harvest (the sequential
        # -flow policy's payoff/feasibility-relevant state), so the replanned
        # policy is the SAME policy, not a reset one. H_1 within the policy's
        # (decrease, increase) tolerances of H_prev.
        dec = flow_coefficient if flow_decrease is None else flow_decrease
        cgen_data = _tighten_period1_harvest(
            cgen_data,
            lb=prev_harvest_mcf * (1.0 - dec) * (1.0 - history_rtol),
            ub=(
                None
                if flow_increase is None
                else prev_harvest_mcf * (1.0 + flow_increase) * (1.0 + HISTORY_RTOL)
            ),
        )

    if fix_period1_harvest_mcf is not None:
        # Fix the period-1 harvest volume to a tight band around the announced
        # value (used by the objective-gap consistency diagnostic to evaluate
        # the announced plan's decision in a subproblem). A tight relative band
        # (not exact equality) so discreteness in achievable harvest doesn't
        # make a genuinely-implementable decision read as infeasible. The band
        # is intersected with any other period-1 bound (carried anchor, cap):
        # the tail-fixed problem is the free problem plus the band (P16.1,
        # #92; previously these writes overwrote each other).
        eps = 0.01
        cgen_data = _tighten_period1_harvest(
            cgen_data,
            lb=fix_period1_harvest_mcf * (1.0 - eps),
            ub=fix_period1_harvest_mcf * (1.0 + eps),
        )

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
    if flow_geometry == "rolling_mean":
        # Rolling-mean NDY: default decrease 0.0 (NDY), NOT the flow_coefficient
        # default (which is the legacy period1 even-flow band tolerance).
        dec = 0.0 if flow_decrease is None else flow_decrease
        _add_rolling_mean_flow(
            problem,
            model,
            window=flow_window,
            flow_key=flow_key,
            flow_decrease=dec,
            realized_history=realized_history,
            history_rtol=history_rtol,
        )
    return problem


def _add_rolling_mean_flow(
    problem: object,
    model: ws3.forest.ForestModel,
    *,
    window: int,
    flow_key: str,
    flow_decrease: float = 0.0,
    realized_history: tuple[float, ...] | None = None,
    history_rtol: float = HISTORY_RTOL,
) -> None:
    """Add backwards-facing rolling-mean NDY rows to a compiled problem (E4, P12).

    For each period ``t >= 1``: ``H_t >= (1 - flow_decrease) * mean(H_window)``,
    where the window covers the ``window`` periods before ``t``. Positions in
    the window that fall before the subproblem's present (period < 1) take
    *realized* past harvests from ``realized_history`` (most recent last) as
    constants on the right-hand side (the realized-history anchoring reading);
    with ``realized_history=None`` only within-plan periods enter (the
    within-plan reading; partial windows at the horizon start average the
    available periods). ``window=1`` degenerates exactly to pointwise
    consecutive-period NDY.

    Coefficients are recovered from the compiled problem via ws3's own cflw
    worker (so they match the compiled matrix exactly) and rows are added with
    ``problem.add_constraint``. This relies on pinned-ws3 internals
    (``problem.trees``, ``problem._leaf_ids``); noted as a fidelity caveat.
    """
    from ws3 import opt
    from ws3.forest import worker_cmp_cflw_batch

    periods = list(model.periods)
    results = worker_cmp_cflw_batch((list(problem.trees.items()), [flow_key], periods))
    mu: dict[int, dict] = {t: {} for t in periods}
    for t, _o, i, j, val in results:
        mu[t][(i, j)] = val
    xnames = {k: f"x_{v}" for k, v in problem._leaf_ids.items()}
    hist = list(realized_history or [])
    for t in periods:
        if t == 1 and not hist:
            continue  # no window before the first period of a fresh plan
        terms = []
        for p in range(t - window, t):
            if p >= 1:
                terms.append(("var", p))
            elif 1 - p <= len(hist):
                # p <= 0 is before this plan's present: relative period 0 is the
                # most recent realized harvest (hist[-1]), -1 the one before.
                # (P17.1, #102: this read hist[p], so p = 0 took the oldest.)
                terms.append(("const", hist[p - 1]))
        if not terms:
            continue
        n = len(terms)
        scale = (1.0 - flow_decrease) / n
        coeffs: dict[str, float] = {}
        rhs = 0.0
        for ij, v in mu.get(t, {}).items():
            coeffs[xnames[ij]] = coeffs.get(xnames[ij], 0.0) + v
        for kind, ref in terms:
            if kind == "var":
                for ij, v in mu.get(ref, {}).items():
                    coeffs[xnames[ij]] = coeffs.get(xnames[ij], 0.0) - scale * v
            else:
                rhs += scale * float(ref) * (1.0 - history_rtol)
        problem.add_constraint(f"flw-rm_{t:03d}_{flow_key}", coeffs, opt.SENSE_GEQ, rhs)


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
