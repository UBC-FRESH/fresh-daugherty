# E3 extension write-up — value-denominated flow constraints (P11, corrected in P14)

Draft for transfer to the manuscript's Extensions section (see
`planning/manuscript-expansion-plan.md` in `fresh_daugherty_manuscript`).
Every number regenerates via
`PYTHONPATH=src python scripts/analyze_p11_value_flow.py`
(tables T1–T4 as CSV+MD, figure F1 as PDF, this directory), reading the
tracked E3 grid records
(`results/experiments/grid_value_flow{,_trajectories,_gaps}.csv`, 864 cells:
18 landbases x 4 rates x 6 policies x 2 denominators, each with the
objective-gap diagnostic and dual volume+revenue trajectory records).

> **Correction (P14, issue #75).** The E3 records first committed in
> `8cf2aa8` were produced by code that announced the *volume*-denominated
> plan in every revenue-denominated cell (`open_loop_projection` was called
> without `flow_denominator`; root cause in #76). The revenue cells therefore
> compared the revenue policy's realized path with the wrong plan, and the
> period-1 invariant failed in 322/360 flow-constrained revenue cells. The
> records were regenerated at `83c7b16` (period-1 invariant now holds in all
> 864 cells; volume cells bit-identical to the previous records and to the
> core grid). **The headline conclusion of the earlier write-up — revenue
> denominating makes inconsistency more pervasive and the CM-CE filler is
> "the tell, not the fuel" — is reversed by the corrected records.** This
> document reports the corrected results.

## Question

If the bounded-deviation flow constraint is denominated in *undiscounted net
revenue* instead of volume, is dynamic inconsistency mitigated or eliminated?
The motivating hypothesis was the filler channel: under a volume NDY,
negatively valued CM-CE area can enter the open-loop basis as
constraint-filler (it *adds* volume); under a revenue NDY such area
*subtracts* from the constrained quantity and can never relax the floor. If
inconsistency persists under value-flow it must come through the
positive-value strata and the state transition alone; if it falls, the
filler channel is an operative contributor.

## Headline result

Revenue denominating **mitigates** inconsistency overall, without eliminating
it, and the effect differs by policy form.

- Flow-constrained occurrence falls from 263/360 (73.1%) under volume to
  200/360 (55.6%) under revenue; mean volume-trajectory magnitude falls from
  0.117 to 0.108.
- By policy (Table T1): NDY 86% → 40%; bounded decline −10% 71% → 38% and
  −20% 58% → 40%; symmetric bounded deviation rises slightly, ±10% 71% → 75%
  and ±20% 79% → 85%.
- By rate (Table T2, all cells incl. NHF): identical at 0% (100%, the
  flat-objective band) and 2% (47–48%); lower under revenue at 4% (31% vs
  50%) and 6% (32% vs 71%).
- The NHF identity check (Table T3) validates the plumbing: with no flow
  constraint the denominator is irrelevant (occurrence 37.5%, magnitude
  0.1318 in both).
- The objective-gap diagnostic confirms the remaining divergence is genuine:
  in flow-constrained revenue cells 64.7% of replan tails are non-optimal
  (58.5% strictly suboptimal, 6.2% infeasible) vs 72.9% under volume. Under
  NDY the infeasible share drops from 50.2% (volume) to 6.7% (revenue) and
  the strictly suboptimal share rises from 40.1% to 68.8%.

## The filler channel

The CM-CE test (Table T4, focal open-loop solves; unaffected by the defect)
confirms that revenue denominating disables the channel:

- Landbase 1 (CM-CE present), volume NDY: the open-loop plan schedules
  3,970–5,334 MCF of negatively valued CM-CE harvest (2.5–3.5% of projected
  volume at 0%/4%).
- Landbase 1, revenue NDY: CM-CE harvest is **zero**.
- Landbase 2 (CM-CE excluded): zero under both denominators (control).

The paired landbases show what the channel contributes. Landbases 1, 3, 5, 7
contain CM-CE and landbases 2, 4, 6, 8 are the same forests without it:

| flow-constrained occurrence | with CM-CE (1, 3, 5, 7) | without CM-CE (2, 4, 6, 8) |
| --- | --- | --- |
| volume denominator | 77/80 | 51/80 |
| revenue denominator | 58/80 | 56/80 |

Under volume, the presence of negatively valued strata raises occurrence
substantially; under revenue, where they cannot enter as filler, the
difference disappears. The negatively valued strata therefore *contribute*
to inconsistency through the filler channel — they are not merely a marker —
but they are not its only source: with the channel disabled, about 70% of
flow-constrained cells on these landbases remain inconsistent, and the gap
diagnostic shows those tails to be genuinely suboptimal.

Fig. F1 shows landbase 1 at 4%: the revenue-NDY plan front-loads (period-1
harvest 13,707 MCF vs 10,245 under volume NDY), because with 1%/yr price
escalation a level *revenue* promise permits declining volume.

## Interpretation for the paper

E3 qualifies the causal attribution rather than sharpening it in one
direction. The unit in which the flow promise is denominated matters: a
revenue promise roughly halves the occurrence of inconsistency under NDY and
bounded-decline policies, and removes the additional inconsistency associated
with negatively valued strata, while symmetric bounded-deviation policies are
slightly more inconsistent under revenue. Inconsistency persists under every
revenue-denominated policy, so the between-period link remains a source of
non-credible plans in either unit.

## Notes and caveats

- Revenue coefficients use the same absolute-calendar-year escalated net
  prices as the objective; the flow revenue is deliberately *undiscounted*
  (the policy's accounting unit, not the planner's objective).
- Occurrence is scored on the volume trajectory for comparability with the
  core grid; the revenue-trajectory magnitudes are reported alongside (T1/T2)
  and lead to the same conclusions.
- Under escalating prices a revenue-level plan has declining volume by design;
  volume divergence measures the departure of the realized path from the
  announced revenue-NDY plan, which is the intended comparison.
