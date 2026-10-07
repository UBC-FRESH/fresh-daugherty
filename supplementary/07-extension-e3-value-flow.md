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
flow-constrained occurrence 181/360
(50%, revenue) vs
203/360 (56%,
volume); mean magnitude 0.093 vs
0.088. The effect differs by policy form
(table below): NDY and bounded decline fall sharply, symmetric bounded
deviation rises slightly. Revenue NDY drives projected CM-CE harvest to
exactly zero (vs 0.0%-5.3% of projected volume under volume NDY on
landbase 1), and on the paired landbases (with vs without CM-CE) the extra
inconsistency associated with negatively valued strata disappears under
revenue denominating; inconsistency persists through the remaining strata.
See the writeup's Table T4 and paired-landbase table.

![Landbase 1 at 4%: NDY by flow-row denominator](figures/e3_ndy_by_denominator.png)

## Occurrence and magnitude by denominator and policy (flow-constrained)

| flow_denominator | flow_policy | occurrence | mean_abs_rel_deviation |
| --- | --- | --- | --- |
| revenue | +/-10% | 0.5 | 0.09 |
| revenue | +/-20% | 0.875 | 0.131 |
| revenue | -10% | 0.333 | 0.078 |
| revenue | -20% | 0.444 | 0.093 |
| revenue | NDY | 0.361 | 0.073 |
| volume | +/-10% | 0.514 | 0.079 |
| volume | +/-20% | 0.639 | 0.1 |
| volume | -10% | 0.375 | 0.076 |
| volume | -20% | 0.431 | 0.098 |
| volume | NDY | 0.861 | 0.087 |
