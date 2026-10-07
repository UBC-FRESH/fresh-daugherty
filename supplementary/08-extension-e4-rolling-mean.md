# 08 — E4: Rolling-mean NDY

Does flooring each period's harvest at the backwards-facing rolling 2- or
3-period mean (instead of the previous period's level) change inconsistency?
Grid: 288 cells (18 landbases x 4 rates x windows {2, 3} x both anchoring
readings). Records: [summary](../results/experiments/grid_rolling_mean.csv) /
[trajectories](../results/experiments/grid_rolling_mean_trajectories.csv) /
[gaps](../results/experiments/grid_rolling_mean_gaps.csv).
Analysis writeup: [p12 writeup](../results/analysis/p12_rolling_mean/writeup.md).

## Headline

Constraint SHAPE is not the operative margin: within-plan rolling-mean
occurrence 87% vs pointwise NDY (86%). The ANCHORING
INSTITUTION is: realized-history anchoring mitigates (occurrence
35%, magnitude 0.050)
but the floor cannot be held exactly in 52% of replans
(mean relax_share), where it is loosened minimally (median
0.9%, maximum 3% of the floor; dropped in
0 replans) — the declining-NDY mechanism as small, persistent
shortfalls.

![Landbase 1 at 4%: pointwise NDY vs rolling-mean readings](figures/e4_rolling_vs_pointwise.png)

## By anchoring reading and window

| anchoring | flow_window | occurrence | mean_abs_rel_deviation | relax_share |
| --- | --- | --- | --- | --- |
| realized-history | 2 | 0.347 | 0.05 | 0.519 |
| realized-history | 3 | 0.347 | 0.05 | 0.528 |
| within-plan | 2 | 0.861 | 0.082 | 0.0 |
| within-plan | 3 | 0.875 | 0.085 | 0.0 |
