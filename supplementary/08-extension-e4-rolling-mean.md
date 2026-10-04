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
occurrence 89% ≈ pointwise NDY (86%). The ANCHORING
INSTITUTION is: realized-history anchoring mitigates (occurrence
66%, magnitude 0.070)
but the floor cannot be sustained in 19% of replan
periods (mean relax_share) — the declining-NDY mechanism as recorded
infeasibility.

![Landbase 1 at 4%: pointwise NDY vs rolling-mean readings](figures/e4_rolling_vs_pointwise.png)

## By anchoring reading and window

| anchoring | flow_window | occurrence | mean_abs_rel_deviation | relax_share |
| --- | --- | --- | --- | --- |
| realized-history | 2 | 0.639 | 0.067 | 0.171 |
| realized-history | 3 | 0.681 | 0.073 | 0.206 |
| within-plan | 2 | 0.889 | 0.1 | 0.0 |
| within-plan | 3 | 0.889 | 0.102 | 0.0 |
