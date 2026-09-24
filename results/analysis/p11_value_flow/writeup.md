# E3 extension write-up — value-denominated flow constraints (P11)

Draft for transfer to the manuscript's Extensions section (see
`planning/manuscript-expansion-plan.md` in `fresh_daugherty_manuscript`).
Every number regenerates via
`PYTHONPATH=src python scripts/analyze_p11_value_flow.py`
(tables T1–T4 as CSV+MD, figure F1 as PDF, this directory), reading the
tracked E3 grid records
(`results/experiments/grid_value_flow{,_trajectories,_gaps}.csv`, 864 cells:
18 landbases x 4 rates x 6 policies x 2 denominators, each with the
objective-gap diagnostic and dual volume+revenue trajectory records).

## Question

If the bounded-deviation flow constraint is denominated in *undiscounted net
revenue* instead of volume, is dynamic inconsistency mitigated or eliminated?
The motivating hypothesis was the filler channel: under a volume NDY,
negatively-valued CM-CE area can enter the open-loop basis as
constraint-filler (it *adds* volume), and those allocations are abandoned
under replanning; under a revenue NDY such area *subtracts* from the
constrained quantity and can never relax the floor — so if the filler
channel were the operative mechanism, revenue denominating should remove the
inconsistency.

## Headline result

The opposite: revenue denominating makes inconsistency strictly *more*
pervasive. Flow-constrained occurrence rises to 98–100% under revenue
NDY/bounded-deviation policies (Table T1: NDY 100% vs 86% volume;
+/-10% 100% vs 71%; -10%/-20% ~99% vs 58–71%), and mean magnitude roughly
doubles. The rate-independence pattern is unchanged (Table T2: 100% at 0%
in both denominators). The NHF identity check (Table T3) validates the
plumbing: with no flow constraint the denominator is irrelevant and the
volume/revenue rows are identical (occurrence 37.5% — the known low-rate
tie-churn band, adjudicated by the gap diagnostic).

## The filler channel: the tell, not the fuel

The CM-CE test (Table T4) confirms the mechanism exactly as theorized:

- Landbase 1 (CM-CE present), volume NDY: the open-loop plan schedules
  3,970–5,334 MCF of negatively-valued CM-CE harvest (2.5–3.5% of projected
  volume at 0%/4%) — the inconsistent-variable filler.
- Landbase 1, revenue NDY: CM-CE harvest is **zero** — the filler channel is
  structurally disabled, as predicted.
- Landbase 2 (CM-CE excluded): zero under both denominators (control).

Yet the revenue-denominated cells are *more* inconsistent, not less. So the
filler variables are the **tell** (a direct, observable marker of the
inconsistency), not the **fuel**: the fuel is the between-period flow link
interacting with the disequilibrium forest state, and it operates through
the positive-value strata alone when the filler is unavailable. Fig. F1
shows why revenue denominating is worse on landbase 1: the revenue-NDY plan
front-loads harder (period-1 realized ~13,300 MCF vs ~10,250 under volume
NDY), because with 1%/yr price escalation a level *revenue* promise permits
declining volume — and the re-solving planner takes the early high-value
volume and abandons the tail all the same.

## Interpretation for the paper

E3 sharpens the causal attribution. The unit in which the flow promise is
denominated is not the operative margin: volume or dollars, the
bounded-deviation link produces non-credible plans. And the negatively
valued strata — the thesis's "inconsistent variables" — are confirmed as an
observable symptom rather than the cause: remove them from the solution
entirely (revenue NDY) and the announced plan is still not followed.

## Notes and caveats

- Revenue coefficients use the same absolute-calendar-year escalated net
  prices as the objective; the flow revenue is deliberately *undiscounted*
  (the policy's accounting unit, not the planner's objective).
- Dual-denominator trajectory records in the E3 grid let every cell be
  scored on both volume and revenue divergence (both are reported).
