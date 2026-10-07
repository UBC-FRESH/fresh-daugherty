# 05 — E1: Time-varying discount-rate shapes

Does a *declining* discount rate mitigate or eliminate dynamic
inconsistency? Paths: linear 4%->0%, linear 6%->0%, inverse-j 4% (hold 1 or
2 periods, then halve per period). Grid: 432 cells (4 paths x 18 landbases x
6 policies), each with the gap diagnostic. Records:
[summary](../results/experiments/grid_discount_paths.csv) /
[trajectories](../results/experiments/grid_discount_paths_trajectories.csv) /
[gaps](../results/experiments/grid_discount_paths_gaps.csv).
Analysis writeup: [p9 writeup](../results/analysis/p9_discount_shapes/writeup.md).

## Headline

Declining rates make inconsistency MORE pervasive, not less: flow-constrained
occurrence is 95% across the E1 paths, with mean
magnitude 0.17 (constant rates, by
rate: 0%: 0.19, 2%: 0.05, 4%: 0.05, 6%: 0.06). The flow-unconstrained control under declining paths
diverges at 100% occurrence, consistent with the
preference-level (Strotz) channel of re-applying a declining schedule from each
planner's present, but not separated here from the low-rate rolling-horizon
effect (the control at a constant 0% rate: 100%).

![Occurrence and magnitude by discount scheme](figures/e1_occurrence_magnitude.png)

![Landbase 1 NDY realized trajectories under declining paths](figures/e1_landbase1_ndy.png)

## Occurrence and magnitude by path (flow-constrained cells)

| discount_path | occurrence | mean_abs_rel_deviation |
| --- | --- | --- |
| invj-4pc-k1 | 1.0 | 0.224 |
| invj-4pc-k2 | 1.0 | 0.253 |
| linear-4pc-0pc | 0.9 | 0.103 |
| linear-6pc-0pc | 0.9 | 0.091 |
