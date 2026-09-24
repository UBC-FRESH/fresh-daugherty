# E1 extension write-up — time-varying discount-rate shapes (P9)

Draft for transfer to the manuscript's Extensions section (see
`planning/manuscript-expansion-plan.md` in `fresh_daugherty_manuscript`).
Every number regenerates from the tracked records via
`PYTHONPATH=src python scripts/analyze_p9_discount_shapes.py`
(tables T1–T4 as CSV+MD, figures F1–F2 as PDF, this directory).

## Question

Does a *declining* discount rate mitigate — or eliminate — the dynamic
inconsistency of the flow-constrained open-loop plan? The core result was
that occurrence is rate-independent across the thesis's four *constant*
rates (the uniform factor cancels out of the consistency conditions). E1
tests time-varying shapes: two linear paths (4%→0%, 6%→0% over the horizon)
and two inverse-j paths (constant 4% for 1 or 2 periods, then exponential
decay halving per period). All four paths start at or near the thesis's
rates and decline, i.e. they weight the far future *more* heavily than the
constant-rate control.

## Headline result

Declining rates do not mitigate the phenomenon; they make it strictly more
pervasive. Flow-constrained occurrence is 98–100% under every E1 path
(Table T1), against 47–86% at the constant 2–6% rates; mean magnitude under
the paths (0.16–0.20) is two to three times the constant 2–6% magnitude
(0.07–0.11), approaching the constant-0% level (0.22). On the all-mature
landbase under NDY (Fig. F2) the realized trajectories under the declining
paths track the announced level flow for roughly the periods while the
rate is still high, then depart — mostly downward — exactly as under the
constant-rate case.

## The Strotz separation: a second, preference-level channel

The no-harvest-flow (NHF) control cells separate the mechanisms (Table T4).
Under constant 4–6% rates the no-flow control is *consistent* (occurrence
0%, magnitude 0.000) — without the flow constraint the problem decomposes
and open-loop and sequential solutions coincide. Under the declining paths,
the same no-flow cells diverge at **100% occurrence** with magnitudes
0.26–0.43 — comparable to or larger than the constant-0% tie-churn case.

This divergence is *genuine* inconsistency, not alternate optima: the
objective-gap diagnostic (Table T3) shows the announced tail strictly
suboptimal in 30–61% of tail periods (and infeasible in 7–14%), with
positive objective gaps — unlike the constant-0% case, where the flat
objective admits near-tie optima that the gap diagnostic shows remain
optimal. With a declining rate the objective is not flat, so a strictly
suboptimal announced tail means the replanner's *own re-started path* makes
a different trade-off than period-0's path did: each replanning planner
re-applies the declining path from her own present (relative indexing), and
is therefore more impatient about her near term than the period-0 planner
was about that same calendar period. This is textbook preference-level
(Strotz) time inconsistency, arising here *on top of* the structural
flow-constraint channel — and it is the whole story in the no-flow cells,
where the structural channel is absent by construction.

Under flow constraints both channels operate: tail periods are strictly
suboptimal or infeasible in 72–90% of cases across the four paths
(Table T3), versus the constant-rate control where the paper's landbase-1
NDY diagnostic showed 13–14 of 15 replan periods strictly suboptimal or
infeasible.

## Interpretation for the paper

The core paper's discount-rate nuance — "discount-rate policy is not a
remedy for non-credible plans" — strengthens. Not only does the *level* of
a constant rate not govern occurrence; *declining* schedules of the kind
advocated for long-horizon public decisions do not restore credibility
either, and by construction add a preference-level inconsistency channel
that operates even where no flow constraint exists. Where the constant-rate
analysis showed occurrence is rate-independent, the extension shows the
*shape* of the rate path matters — in the direction of making plans less
credible, not more.

## Notes and caveats

- Paths are indexed by each subproblem's relative present (each replanner
  re-applies the path from her own now), matching the stack's convention
  that discounting is relative while price escalation is calendar-absolute.
  A calendar-absolute reading of the declining schedule is a possible
  sensitivity analysis (would remove the preference-drift channel while
  leaving the structural one).
- Magnitudes under declining paths are inflated relative to constant 2–6%
  partly because the effective far-future weighting is higher (closer to
  the 0% flat-objective regime); occurrence, however, is near-total even
  where the path starts at 4–6%.
- Extension grids are additive; the core 432-cell constant-rate grid is the
  unchanged control throughout.
