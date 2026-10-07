# P18 hand-off to the manuscript (issue #114)

Supersedes `planning/p17-manuscript-handoff.md`. Records at `35f6a65` (thesis
terminal constraints on every flow-constrained run; young-age yields follow the
calibrated Chapman-Richards shape below the first FEIS age). Headline basis:
periods 2-11; periods 1-15 in brackets. Sources: `results/analysis/p17_headline/`,
`p17_thesis_comparison/`, `p15_descriptives/`, `p15_metrics/`, `p18_young_yields/`,
`p18_rerun/old_vs_new.md`; detailed extraction log in the P18 issue thread.

## Model (Methods)

- Terminal constraints (thesis p. 77): final-period standing volume >= 80% of the
  average inventory of the forest regulated under each stratum's regeneration
  prescription; final-period harvest <= 120% of its long-term sustained yield;
  highest-PNV rotations; every flow-constrained plan and replan; not NHF, not E2
  (p. 80). Coefficients: ws3's inventory of each column's post-action state.
- Young-age yields: below the first FEIS age (55-175 yr) the cell's calibrated
  Chapman-Richards curve scaled to the first FEIS value (flat hold overstated
  young-stand volume by up to 45% at rotation ages).
- With terminal constraints no flow-constrained plan harvests more than twice
  its earlier mean in period 15 (0/360; was 78/360). Periods 12-15 still carry
  on average 53% (median 47%) of a scenario's summed divergence.

## Core grid

- Flow-constrained 178/360 = 49% [203/360 = 56%], magnitude 0.072 [0.088];
  positive rates 88/270 = 33% [113/270 = 42%].
- NHF control 34/72 = 47%: 0% 18/18, 2% 16/18, 4-6% 0; magnitude 0.17. With a
  fixed horizon 0/72 (both histories): a rolling-horizon effect.
- By rate (flow-constrained): 0% 90/90 (0.16), 2% 26/90 (0.043), 4% 28/90
  (0.038), 6% 34/90 (0.045).
- By policy: NDY 50/72 = 69% (0.077) [62/72 = 86%]; +/-20% 40/72 = 56% (0.077);
  +/-10% 34/72 = 47% (0.062); -20% 28/72 = 39% (0.080); -10% 26/72 = 36% (0.063).
- Tolerance 2/3/5/7.5/10%: 68/61/49/38/26% [82/71/56/42/36%].
- By landbase: occurrence 35-100%; magnitude 1-6: 0.067-0.154; 7-10:
  0.042-0.077; 11-18: 0.042-0.051.
- Paired CM-CE landbases: 67/80 vs 37/80; thesis measure +3.9 points with CM-CE
  (higher in 81% of 36 pairs; thesis p. 116: +3 points).
- Seeds (11-18): 36-41% across draws (tracked 36%), magnitude 0.047-0.050.
- Landbase 1, NDY: announced 8,180 (0%), 8,934 (2%), 8,914 (4%, 6%) MCF/period;
  realized below announced in every later period at every rate; 4%: declines
  steadily to 7,436 by period 11 and 7,037 by period 15; periods 2-11 total vs
  announced -18.8% (0%), -12.1% (2%), -9.5% (4%), -9.1% (6%). Landbase 2:
  below in 14/14 later periods at every rate.

## Objective-gap diagnostic (core, replans in periods 2-11)

- Announced plan strictly suboptimal or infeasible: flow-constrained 58%, NHF
  25% (only at 0-2%). Landbase 1 NDY: 9/10 (0%), 10/10 (2-6%); NHF 1/10 at 0%,
  0 otherwise.
- Every inconsistent scenario (178/178) has such a replan; 146 of 182
  consistent scenarios too. First deviation: 324 scenarios, 40 start
  infeasible; first suboptimal gap median 0.051% of the objective (p90 0.95%).

## Replanning institutions (periods 2-11 [1-15])

| Horizon | History | Flow-constrained | Magnitude | Plan optimal | NHF |
| --- | --- | --- | --- | --- | --- |
| rolling | reset (core) | 178/360 [203] | 0.072 | 42% | 34/72 [34] |
| fixed | reset | 98/360 [88] | 0.046 | 61% | 0/72 [0] |
| rolling | carried | 87/360 [118] | 0.035 | 66% | 34/72 [34] |
| fixed | carried (exact tail) | 1/360 [0] | 0.0003 | 99.9% | 0/72 [0] |

- Exact-tail residual: landbase 8, 0%, -10% (0.061 on periods 2-11; consistent
  on 1-15); only numerical loosening (39 at 1e-5, 1 at 1e-4).
- Rolling/carried: 81 of 87 inconsistent at 0% (4, 1, 1 at 2, 4, 6%); anchor
  materially loosened in 13% of replans.
- Landbase 1 NDY 4%: 0.095 rolling/reset, 0.055 fixed/reset, 0.036
  rolling/carried, 0 exact tail.

## Thesis comparisons (eq. 5-1, periods 2-11; full-choice equivalents of the thesis's sets)

- Landbases 1-6: 7.8% (median 7.6%) vs thesis 11.9% (9.6%); 7-10: 3.4% vs 6.8%;
  11-18: 3.7% vs 5.3%; all 5.3% vs 9.0% (thesis subsets include restricted-choice runs).
- Carried-history test (landbases 1-10, 4%, five flow policies): rolling/carried
  0.55% vs thesis 1.9%; reset 5.2%.
- Table 6.8 populations (4%): NDY 5.4% vs 6.0%; -10% 2.6% vs 15.7%; -20% 2.4%
  vs 16.1%; +/-10% 3.6% vs 7.1%; +/-20% 6.3% vs 8.2%.
- Landbases 5, 6 over matched sets: 10.2%, 6.4% (thesis 19%, 24%, p. 125);
  highest here: landbase 3, 11.3%.
- Reference run (NDY, 4%) vs p. 124 classification: agrees on 1, 2, 3, 5, 7, 10
  (> 5%); disagrees on 4, 6, 8 (< 3%: 2.5, 0.4, 0%) and 9, 11-18 (4.9-6.8%,
  thesis < 3%): 6 of 18.

## Extensions (periods 2-11 [1-15])

- E1: flow-constrained linear 4->0% 55/90 = 61% (0.059), linear 6->0% 35/90 = 39%
  (0.053), inverse-j k=1 90/90 (0.207), k=2 89/90 (0.234) [81, 81, 90, 90];
  constant-rate control 4% 31%, 6% 38%, 0% 100%. NHF control 18/18 under every
  path; NHF replans suboptimal 28-69%, infeasible 0-14%.
- E2: 72/72 converged; 2/72 inconsistent (landbases 11 and 14 at 0%; 0.058,
  0.125); 7/72 with a single period > 5% (max 13.6%); cap binds 98% planned /
  90% realized periods; replans optimal 95.7%, suboptimal 4.3%. Landbase 1 4%:
  cap 7,950 MCF/period (225,100 m3), 11% below announced NDY; vs realized NDY:
  volume +0.7%, NPV -6.1%. Medians vs realized NDY: volume +2.3%, NPV -0.6%
  (ranges -16% to +16%, -9% to +18%).
- E3: revenue 171/360 = 48% (0.081) vs volume 178/360 = 49% (0.072) [181 vs
  203]; revenue-scored 171/360. By policy, volume -> revenue: NDY 50 -> 25;
  -10% 26 -> 22; -20% 28 -> 29; +/-10% 34 -> 36; +/-20% 40 -> 59. Paired
  landbases (revenue) 50/80 vs 45/80. Projected CM-CE share of landbase 1 NDY
  harvest: volume 0% (at 0%) and 5.3% (at 4%); revenue 3.2% and 2.2% (CM-CE is
  no longer excluded under the revenue floor with terminal constraints).
  Revenue-NDY period-1 harvest 82% above volume NDY (landbase 1, 4%: 16,222 vs
  8,914 MCF). Revenue replans non-optimal 60%.
- E4: within-plan 99/144 = 69% (0.083) vs pointwise NDY 69%; realized-history
  39/144 = 27% (0.046) (0%: 33, 2-6%: 2 each); floor loosened beyond numerical
  tolerance in 65% of replans (40% at 0%, 72-74% at 2-6%), median 1.3%, max 2.3%,
  never dropped.

## Statements that change vs the P17-based draft

- Headline 52% -> 49%; positive rates 36% -> 33%; NHF 19/72 -> 34/72, now at
  0-2% (16/18 at 2%), still only under a rolling horizon.
- NDY again the most frequent policy (69%), not +/-20%.
- Exact tail 0 -> 1/360 on periods 2-11.
- Landbase 1 example: announced 8,914, steady decline (classic shape).
- E2: 2/72 inconsistent (not 0); cap 7,950; NPV vs realized NDY -6%.
- E3: no overall mitigation (48% vs 49%); helps only NDY, worsens +/-20%;
  revenue floor no longer excludes CM-CE.
- E4 realized-history 27%, loosening in 65% of replans.
- End-of-horizon liquidation gone (0/360) with terminal constraints.
