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
0.006 — all below the 5% tolerance), with
100% convergence; single periods can still deviate by more than 5% in
1/72 scenarios. The calibrated
level on landbase 1 at 4% (9,110 MCF/period) is 8% below the
NDY plan's *announced* level (9,879). Against what replanned NDY
actually delivers, the cap's total volume differs by
+1.7% and its NPV by
-0.3% (medians over
scenarios; per-scenario spread on page 10).

![Landbase 1 at 4%: NDY flow link vs calibrated cap](figures/e2_ndy_vs_cap.png)

## By discount rate

| discount_rate | occurrence | mean_abs_rel_deviation | calibrated_cap_mcf | converged |
| --- | --- | --- | --- | --- |
| 0.0 | 0.0 | 0.0014 | 10113.5562 | 1.0 |
| 0.02 | 0.0 | 0.0017 | 10373.7233 | 1.0 |
| 0.04 | 0.0 | 0.0013 | 10287.4934 | 1.0 |
| 0.06 | 0.0 | 0.0006 | 10129.1338 | 1.0 |
