# 02 — Core experiment grid (thesis reproduction)

432 cells: 18 landbases x 4 constant discount rates (0/2/4/6%) x 6
harvest-flow policies (Table 5.6: NHF, NDY, -10%, -20%, +/-10%, +/-20%),
each a full sequential-replanning simulation over the 15-period horizon.
Per-cell records: [grid.csv](../results/experiments/grid.csv) and
[grid_trajectories.csv](../results/experiments/grid_trajectories.csv).

## Headline

- Flow-constrained cells: **65%** exhibit dynamic
  inconsistency (mean relative divergence > 5%).
- Flow-unconstrained (NHF) control: **39%**; by
  discount rate 0%: 18/18, 2%: 10/18, 4%: 0/18, 6%: 0/18. Under a fixed horizon the control's
  divergence falls to 2/72 (a rolling-horizon effect; see
  [03](03-gap-diagnostic.md) and [10](10-review-analyses.md)).

## The declining non-declining yield

![The declining non-declining yield](figures/core_declining_ndy.png)

## Occurrence and magnitude by harvest-flow policy

| flow_policy | occurrence | mean_abs_rel_deviation |
| --- | --- | --- |
| +/-10% | 0.611 | 0.089 |
| +/-20% | 0.847 | 0.122 |
| -10% | 0.5 | 0.103 |
| -20% | 0.486 | 0.115 |
| NDY | 0.819 | 0.078 |
| NHF | 0.389 | 0.13 |

Flow-constrained policies only:

| flow_policy | occurrence | mean_abs_rel_deviation |
| --- | --- | --- |
| +/-10% | 0.611 | 0.089 |
| +/-20% | 0.847 | 0.122 |
| -10% | 0.5 | 0.103 |
| -20% | 0.486 | 0.115 |
| NDY | 0.819 | 0.078 |

## Occurrence and magnitude by discount rate

| discount_rate | occurrence | mean_abs_rel_deviation |
| --- | --- | --- |
| 0.0 | 1.0 | 0.258 |
| 0.02 | 0.574 | 0.06 |
| 0.04 | 0.426 | 0.049 |
| 0.06 | 0.435 | 0.058 |
