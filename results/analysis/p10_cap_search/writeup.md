# E2 extension write-up — max-harvest-cap even-flow search (P10)

> **Superseded numbers (P16, #91; 2026-10-05).** This write-up records the
> phase's original reasoning; its numbers predate the P16 re-run (defect fixes
> and landbases rebuilt to thesis p. 79; see `CHANGE_LOG.md`). Current values:
> the tables in this directory (regenerated from the records) and
> `supplementary/06-extension-e2-cap-search.md`; old-vs-new summary in
> `results/analysis/p16_rerun/old_vs_new.md`.


Draft for transfer to the manuscript's Extensions section (see
`planning/manuscript-expansion-plan.md` in `fresh_daugherty_manuscript`).
Every number regenerates from the tracked records via
`PYTHONPATH=src python scripts/analyze_p10_cap_search.py`
(tables T1–T3 as CSV+MD, figure F1 as PDF, this directory).

> **Correction (P14, issue #78).** The E2 records first committed in P10 were
> produced by code that computed the announced plan and the H_max bisection
> bracket at the 4% default discount rate in every cell (`open_loop_projection`
> was called without `discount_rate`). Cells at 0%, 2% and 6% therefore
> announced the 4% plan and bisected from a 4% bracket; the period-1
> invariant failed in 4/72 cells (all at 0%). The records were regenerated at
> `83c7b16` (invariant holds in all 72 cells). Calibrated caps changed only at
> 0% and 2% (median 0%, range −0.32% to +2.93%); 4% and 6% are unchanged.
> The headline (0% occurrence, 100% convergence) is unchanged; the numbers
> below are the corrected ones.

## Question

If the NDY flow *link* is replaced by a simple per-period max-harvest cap,
and the cap is calibrated by iterative re-solve until the **realized**
sequential-replanning trajectory satisfies an even-flow criterion, is the
resulting plan dynamically consistent? The cap removes the between-period
coupling that the core paper identifies as the operative link, so E2 tests
the mechanism directly: no link, no inconsistency — but at what harvest
level, and does the calibrated even flow survive replanning?

## Method

Even-flow criterion (recorded per cell): |OLS trend slope| <= 1% of the mean
per period; max period-over-period relative fluctuation <= 5% of the mean;
coefficient of variation <= 5%. The search bisects the cap between the
unconstrained (NHF) peak period harvest and 0, scoring the *realized*
replanned trajectory at each iteration (open-loop evenness recorded as
secondary), to the loosest cap meeting the criterion (relative tolerance
0.5%, at most 25 iterations). Grid: 18 landbases x 4 constant discount rates
(72 cells), each with the objective-gap diagnostic at the calibrated cap.

## Headline result

The calibrated cap **eliminates** dynamic inconsistency, everywhere. All 72
cells converged; occurrence under the calibrated caps is **0%** at every
discount rate (Table T1), with mean divergence 0.02–0.19% by rate (grid maximum of cell means 0.81%,
all below the 5% occurrence tolerance). Single periods can still deviate:
2/72 cells have one period above 5% (maximum 7.9%). The gap diagnostic confirms this is
genuine consistency rather than tie-breaking: 96.3% of tail periods leave
the announced tail *optimal* (vs. the flow-constrained core, where most
tails are strictly suboptimal or infeasible; e.g. the NDY control runs at
78–100% occurrence). The residual 3.5% suboptimal / 0.2% infeasible tail
periods are noise-level deviations that do not lift any cell past the
occurrence tolerance.

The mechanism is exactly as theorized: with the inter-period link removed,
each replanning subproblem decomposes from the announced plan's tail, the
re-solving planner has no reason to abandon the announced level, and the
open-loop projection becomes a credible forecast (Fig. F1: on landbase 1 at
4%, the NDY plan projects ~10,250 MCF/period and delivers a declining
realized trajectory, while the calibrated cap projects ~9,400 MCF/period and
the realized trajectory sits on it).

## Interpretation for the paper

E2 is the constructive counterpart to the core result and connects directly
 to the remedies discussion: an honest even-flow promise is achievable, but
only at the *calibrated* level — here ~9,400 MCF/period on landbase 1, about
8% below the NDY plan's announced ~10,250 MCF/period that sequential
replanning will not deliver. The cap search is, in effect, an automated
allowable-cut calibration that prices the credibility of the flow promise:
the difference between the announced NDY level and the calibrated even level
is the size of the allowable-cut effect on this landbase. This ties the
thesis's credibility critique to the even-flow/allowable-cut-effect
literature the paper already cites.

## Notes and caveats

- Threshold sensitivity: the calibrated cap depends mildly on the even-flow
  thresholds; defaults are recorded per cell and a sensitivity note is a
  candidate follow-up.
- The criterion is scored on the realized trajectory; scoring the open-loop
  projection alone would under-test credibility (a projection can look even
  while being abandoned).
- The cap is a volume cap; a value-denominated cap interacts with E3 and is
  noted there.
- Open review points for the manuscript (not changed here, P14 scope is the
  records): whether "eliminates" and the allowable-cut-effect reading are
  supported (the cap is calibrated on the realized path; comparison with the
  *realized* NDY volume and NPV is not yet reported).
