# 06 — E2: Max-harvest-cap even-flow search

If the NDY flow link is replaced by a per-period max-harvest cap calibrated
by bisection until the REALIZED replanned trajectory meets an even-flow
criterion (trend, fluctuation, CV thresholds — `src/fresh_daugherty/evenflow.py`),
is the calibrated plan consistent? Grid: 72 cells (18 landbases x 4 rates).
Records: [summary](../results/experiments/grid_cap_search.csv) /
[trajectories](../results/experiments/grid_cap_search_trajectories.csv) /
[gaps](../results/experiments/grid_cap_search_gaps.csv).
Analysis writeup: [p10 writeup](../results/analysis/p10_cap_search/writeup.md).

## Headline

Under the calibrated caps, occurrence is 0% across the
grid (mean divergence 0.001, max
0.008 — all below the 5% tolerance), with
100% convergence; single periods can still deviate by more than 5% in
2/72 cells. The calibrated
level on landbase 1 (~9,400 MCF/period) is ~8% below the NDY plan's
*announced* level; against the volume that replanned NDY actually delivers,
the cap's total volume is about equal (median
-0.5%) and its NPV is
-4.6% (median; page 10).

![Landbase 1 at 4%: NDY flow link vs calibrated cap](figures/e2_ndy_vs_cap.png)

## By discount rate

| discount_rate | occurrence | mean_abs_rel_deviation | calibrated_cap_mcf | converged |
| --- | --- | --- | --- | --- |
| 0.0 | 0.0 | 0.0014 | 8919.7865 | 1.0 |
| 0.02 | 0.0 | 0.0019 | 9138.7519 | 1.0 |
| 0.04 | 0.0 | 0.001 | 9024.0398 | 1.0 |
| 0.06 | 0.0 | 0.0002 | 9030.2152 | 1.0 |
