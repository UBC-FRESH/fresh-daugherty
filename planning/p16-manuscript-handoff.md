# P16 hand-off to the manuscript (issue #98)

> **Superseded (P17, #101).** Numbers below predate the P17 re-run; use
> `planning/p17-manuscript-handoff.md`.


Supersedes `planning/p15-manuscript-handoff.md`. Every number below comes from
the P16 records (core, E1, E2, E3, seeds at `45563fa`; E4 and the institution
grid at `a1bf7c4`) via the tracked analyses (`scripts/analyze_*.py`, re-run by
`scripts/build_supplement.py`). Old-vs-new: `results/analysis/p16_rerun/old_vs_new.md`.

## What changed in the model (state in Methods / Limitations)

| Change | Effect | Where |
| --- | --- | --- |
| Landbases 3–18 rebuilt to thesis p. 79 | 9–18 have no CM-CE; 9/10 intensive prescriptions (5/7; 4/6 on CR-CF), 50/25/25; 3–8 highest-volume first, rx1/rx2 regeneration, rx4 for 7–8's last 30 years | `instance/landbases.py` `LANDBASE_ASSUMPTIONS` |
| CH-CW two-storied mature type | had the sawtimber volume (10.27 vs 4.66 MCF/ac) in landbases 1–8 | `model.py` (#99) |
| Gap diagnostic | period-1 band now intersected with carried anchor / E2 cap | `lp.py` (#92) |
| History bounds | loosened minimally (numerical steps, then bisection to 1e-3), never silently dropped | `replan.py` (#93) |
| Regeneration (decision B) | fixed: mature → planting (rx2), managed → own prescription; no treatment costs or commercial thinnings in the objective; thesis's intensity choice (pp. 28–29, 74, 81) and thinning-termination inconsistency (p. 123) cannot arise | `planning/p16-regen-choice-probe.md` |

## Core grid (`grid.csv`; `p15_descriptives`, `p15_metrics`)

- Flow-constrained: 235/360 (65%), magnitude 0.101. NHF control: 28/72 (39%), magnitude 0.13; by rate 18/18, 10/18, 0/18, 0/18.
- By rate (flow-constrained): 0% 90/90 (0.214); 2% 52/90 (0.063); 4% 46/90 (0.059); 6% 47/90 (0.069). **No rising trend over positive rates** (was 47/60/86%).
- By policy: ±20% 61/72 (85%, 0.122) is the most frequent; NDY 59/72 (82%, 0.078); ±10% 44/72 (61%, 0.089); −10% 36/72 (50%, 0.103); −20% 35/72 (49%, 0.115). NDY has the **smallest** flow-constrained magnitude.
- By landbase: occurrence 45–100%; magnitude 0.074 (lb 12) to 0.164 (lb 3); all-mature/area-control 1–8 0.092–0.164; young growth 9–18 0.074–0.089.
- Paired CM-CE landbases (1,3,5,7 vs 2,4,6,8): 77/80 vs 49/80; magnitude 0.139 vs 0.116.
- Tolerance 2/3/5/7.5/10%: 88/78/65/45/39%.
- Window periods 2–11: 187/360 (52%), magnitude 0.080; periods 12–15 carry mean 56% (median 52%) of summed divergence.
- Thesis volume inconsistency (eq. 5-1, periods 2–11), thesis-matched subset (n = 144): mean 5.8%, median 4.9%, > 6% 35%, > 10% 12% — **below** the thesis's 9.0%, 7.2%, 60%, 27% (pp. 92, 124). All 360 flow-constrained: mean 9.2%, median 5.5%.
- Landbase 1, NDY: total realized vs announced −15.9% (0%), −8.5% (2%), −5.7% (4%), −5.1% (6%). At 4%: announced 9,879 MCF/period; realized below it in every period 2–15, dipping to 7,493 in periods 5–6, ~9,700 in 7–12, 8,319 in 15; mean divergence 0.057.
- Seeds (landbases 11–18, flow-constrained): occurrence 47–56% across five draws (tracked draw 51%), magnitude 0.079–0.085.

## Objective-gap diagnostic (core institution; `p15_gaps`)

- Replans with the announced plan strictly suboptimal or infeasible: flow-constrained 62% (optimal 22% at 0%, 38% at 2%, 46% at 4%, 45% at 6%); NHF 23% (optimal 41% at 0%, 66% at 2%, 100% at 4–6%).
- By policy, optimal share: NDY 15%, ±20% 29%, ±10% 34%, −10% 55%, −20% 56%, NHF 77%.
- First deviation per flow-constrained scenario: 359/360 have one; 79 start infeasible; first suboptimal gap median 0.085% of the replan objective (p90 3.6%); median first period 5.
- Gap-based occurrence 359/360 (materiality ≤ 0.1%), 356/360 (1%) vs metric 235/360; 124 of the 125 metric-consistent scenarios carry a flagged deviation.
- NHF: 28/72 scenarios with a gap ≥ 1% or infeasible.

## Replanning institutions (`p15_institutions`)

| Horizon | Flow history | Flow-constrained | Magnitude | Plan optimal | NHF |
| --- | --- | --- | --- | --- | --- |
| rolling | reset (core) | 235/360 (65%) | 0.101 | 38% | 28/72 |
| fixed | reset | 147/360 (41%) | 0.076 | 57% | 2/72 |
| rolling | carried | 118/360 (33%) | 0.065 | 58% | 28/72 |
| fixed | carried (exact tail) | 4/360 (1%) | 0.002 | 99.7% | 2/72 |

- Exact tail: the 4 residual scenarios are all at 0% under −20% (landbases 12, 13, 15, 18; magnitude 0.050–0.055, just above tolerance); no material relaxation (53 numerical loosenings of 1e-5).
- Rolling/carried: anchor materially relaxed in 8.7% of replans.
- Landbase 1, NDY, 4%: 0.057 (rolling/reset), 0.059 (fixed/reset), 0.000 (both carried).
- Ranking holds at every tolerance 2–10% (exact tail ≤ 3.6%).

## Extensions

- E1 (`grid_discount_paths.csv`): flow-constrained 349/360 (97%); by path linear 4→0% 97% (0.136), linear 6→0% 91% (0.126), inverse-j k=1 100% (0.200), k=2 100% (0.176). Constant-rate control 0.059 (4%), 0.069 (6%), 0.214 (0%). NHF control 72/72 under every path; NHF tails strictly suboptimal 27–53%, infeasible 7–29% of replans.
- E2 (`grid_cap_search*`): 72/72 converged, 0/72 inconsistent, mean 0.0013, max 0.006; 1/72 with a single period > 5% (max 6.9%). Tails optimal 95.9%, infeasible 2.8%, suboptimal 1.3%. Landbase 1 at 4%: cap 9,110 MCF/period, 7.8% below announced NDY (9,879); vs realized NDY total volume −2.5%, NPV −3.9%. Medians over scenarios: volume +1.7%, NPV −0.3% vs realized NDY (at 0%: +9.8% / +9.8%; positive rates: volume +1.1 to +2.5%, NPV +0.4 to −0.9%); vs announced NDY −9.6%.
- E3 (`grid_value_flow.csv`): revenue 190/360 (53%, 0.102) vs volume 235/360 (65%, 0.101). By policy (volume → revenue): NDY 82% → 36%; −10% 50% → 32%; −20% 49% → 40%; ±10% 61% → 74%; ±20% 85% → 82%. Paired landbases revenue 54/80 vs 52/80. CM-CE share of landbase 1's projected volume-NDY harvest 0.9% (0%) and 3.6% (4%); zero under revenue NDY.
- E4 (`grid_rolling_mean.csv`): within-plan 121/144 (84%, 0.083) vs pointwise NDY 82%; realized-history 57/144 (40%, 0.058); floor loosened in 52% of replans (9% at 0%, 65–66% at 2–6%), median loosening 1.0%, max 22%, never dropped.

## Statements that no longer hold (manuscript draft X45)

- "Occurrence rises with the rate over positive rates (47/60/86%)" — no.
- "Non-declining yield is the most frequently inconsistent policy" — ±20% is (85% vs 82%).
- "Our reproduction matches the thesis's average magnitude (8.2% vs 9.0%)" — now 5.8% vs 9.0%.
- E2 "about the same volume, 3–7% lower NPV" — now +1.7% volume, −0.3% NPV (medians), landbase 1 −2.5% / −3.9%.
- E4 "relaxation in 19% (27% at 6%)" — now minimal loosening in 52% (median 1%).
- Landbase 2 "below every young-growth landbase" — now the reverse (0.092 vs 0.074–0.089).
- Landbase 1 figure: dip-and-recover shape, not a steady decline.
