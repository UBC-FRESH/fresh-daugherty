# 07 — E3: Value-denominated flow constraints

Does denominating the bounded-deviation flow constraint in undiscounted net
revenue (instead of volume) mitigate or eliminate inconsistency? Grid: 864
cells (18 landbases x 4 rates x 6 policies x 2 denominators), each with the
gap diagnostic and dual volume+revenue trajectory records. Records:
[summary](../results/experiments/grid_value_flow.csv) /
[trajectories](../results/experiments/grid_value_flow_trajectories.csv) /
[gaps](../results/experiments/grid_value_flow_gaps.csv).
Analysis writeup: [p11 writeup](../results/analysis/p11_value_flow/writeup.md).

> Correction (P14, issue #75): the E3 records were regenerated after a defect
> that announced the volume-denominated plan in revenue-denominated cells; the
> earlier conclusion (revenue denominating worsens inconsistency) is reversed.

## Headline

Revenue denominating MITIGATES inconsistency without eliminating it:
flow-constrained occurrence 190/360
(53%, revenue) vs
235/360 (65%,
volume); mean magnitude 0.102 vs
0.101. The effect differs by policy form
(table below): NDY and bounded decline fall sharply, symmetric bounded
deviation rises slightly. Revenue NDY drives projected CM-CE harvest to
exactly zero (vs 0.9%-3.6% of projected volume under volume NDY on
landbase 1), and on the paired landbases (with vs without CM-CE) the extra
inconsistency associated with negatively valued strata disappears under
revenue denominating; inconsistency persists through the remaining strata.
See the writeup's Table T4 and paired-landbase table.

![Landbase 1 at 4%: NDY by flow-row denominator](figures/e3_ndy_by_denominator.png)

## Occurrence and magnitude by denominator and policy (flow-constrained)

| flow_denominator | flow_policy | occurrence | mean_abs_rel_deviation |
| --- | --- | --- | --- |
| revenue | +/-10% | 0.736 | 0.113 |
| revenue | +/-20% | 0.819 | 0.134 |
| revenue | -10% | 0.319 | 0.096 |
| revenue | -20% | 0.403 | 0.104 |
| revenue | NDY | 0.361 | 0.064 |
| volume | +/-10% | 0.611 | 0.089 |
| volume | +/-20% | 0.847 | 0.122 |
| volume | -10% | 0.5 | 0.103 |
| volume | -20% | 0.486 | 0.115 |
| volume | NDY | 0.819 | 0.078 |
