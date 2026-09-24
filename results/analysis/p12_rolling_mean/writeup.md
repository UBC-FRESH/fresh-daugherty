# E4 extension write-up — rolling-mean NDY (P12)

Draft for transfer to the manuscript's Extensions section (see
`planning/manuscript-expansion-plan.md` in `fresh_daugherty_manuscript`).
Every number regenerates via
`PYTHONPATH=src python scripts/analyze_p12_rolling_mean.py`
(tables T1–T4 as CSV+MD, figure F1 as PDF, this directory), reading the
tracked E4 grid records
(`results/experiments/grid_rolling_mean{,_trajectories,_gaps}.csv`, 288 cells:
18 landbases x 4 rates x windows {2, 3} x both anchoring readings, each with
the objective-gap diagnostic).

## Question

Does flooring each period's harvest at the backwards-facing rolling 2- or
3-period mean (instead of the previous period's level) change
dynamic-inconsistency behaviour? The rolling mean damps the pointwise NDY
ratchet: a temporary dip is permitted as long as the average holds. And
because the window is backwards-facing, it forces the question of *which*
history the floor references — the within-plan projection or the realized
past — which turns out to be the operative margin.

## Headline results

1. **Constraint shape alone changes nothing.** Under the within-plan
   anchoring (each replan re-anchors freely, the paper's fresh-constraint
   institution), the rolling-mean NDY behaves like pointwise NDY: occurrence
   89% vs 86% control, mean magnitude 0.10 vs 0.10 (Table T4). Smoothing the
   reference level does not mitigate — the shape of the floor is not the
   operative margin.
2. **The anchoring institution is.** Under the realized-history reading
   (each replan's early periods floored by what actually happened),
   occurrence drops to 65–72% and magnitude to ~0.07 (Tables T1–T2) — real
   mitigation, not elimination. The cost: the floor frequently cannot be
   sustained from the depleted realized state, so the policy must *relax* —
   19–32% of replan periods at positive rates (relax_share; the
   declining-non-declining-yield mechanism surfacing as recorded
   infeasibility rather than silent abandonment).
3. The gap diagnostic (Table T3) confirms the residual within-plan
   divergence is genuine (announced tails strictly suboptimal/infeasible),
   and Fig. F1 shows the contrast on landbase 1 at 4%: the realized-history
   trajectory holds the announced level far longer, with visible
   relax-and-recover dips, while the within-plan trajectory tracks the
   declining NDY path.

## Interpretation for the paper

E4 refines the mechanism attribution one step further than E1–E3. The
inconsistency is not an artifact of the pointwise link's strictness
(E4 within-plan ≈ NDY), nor of the discount rate's level (core) or shape
(E1), nor of the constraint's denomination (E3). It is the conjunction of
(a) *some* binding inter-period promise and (b) the replanning institution
that lets each future planner re-anchor that promise to her own present.
When the institution instead binds the future planner to realized history,
the promise is enforced — but the disequilibrium forest often cannot deliver
it, and the policy relaxes. Both readings are defensible models of planning
practice; the paper's methods discussion of the anchoring convention
(currently a robustness note) becomes a result in its own right.

## Notes and caveats

- The rolling-mean rows are added post-compile via ws3's cflw coefficient
  machinery (pinned-ws3 internals); k=1 degenerates exactly to pointwise
  NDY (regression-tested).
- Relax events are recorded per period (`solver_note` /
  `relax_share`) — infeasibility is reported, not hidden.
- Windows k ∈ {2, 3} give near-identical results (Table T1); longer windows
  are a possible sensitivity note.
