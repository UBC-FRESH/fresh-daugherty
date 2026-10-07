# 10 — Review analyses (P15)

Analyses added in response to a pre-submission review (fresh-daugherty P15,
issue #82). Every table regenerates from the tracked records via the
`scripts/analyze_p15_*.py` scripts (re-run by this builder). Records:
[institution grid](../results/experiments/grid_institutions.csv) /
[seed grid](../results/experiments/grid_seeds.csv); core, E2-E4 records as in
pages 02 and 06-08.

## Replanning institution

Flow-constrained occurrence: rolling horizon + reset flow history (the core
grid) 263/360 (73%); fixed horizon + reset 219/360 (61%);
rolling + carried 138/360 (38%); fixed horizon + carried history
(each replan solves the exact tail of the original problem)
6/360 (2%). A null test (CI) confirms that fixed + carried
replanning from the plan's own state reproduces the plan.

| horizon_institution | flow_history | inconsistent | cells | occurrence | mean_magnitude | relax_share |
| --- | --- | --- | --- | --- | --- | --- |
| fixed | carried | 6 | 360 | 0.0167 | 0.0034 | 0.0083 |
| fixed | reset | 219 | 360 | 0.6083 | 0.0973 | 0.0 |
| rolling | carried | 138 | 360 | 0.3833 | 0.068 | 0.0262 |
| rolling | reset | 263 | 360 | 0.7306 | 0.1173 | 0.0 |

NHF control by institution:

| horizon_institution | flow_history | inconsistent | cells | mean_magnitude |
| --- | --- | --- | --- | --- |
| fixed | carried | 4 | 72 | 0.0046 |
| fixed | reset | 4 | 72 | 0.0046 |
| rolling | carried | 27 | 72 | 0.1318 |
| rolling | reset | 27 | 72 | 0.1318 |

Gap-diagnostic tail status by institution (flow-constrained, periods > 1):

| horizon_institution | flow_history | infeasible | optimal | suboptimal |
| --- | --- | --- | --- | --- |
| fixed | carried | 0.003 | 0.989 | 0.008 |
| fixed | reset | 0.033 | 0.437 | 0.531 |
| rolling | carried | 0.099 | 0.868 | 0.033 |
| rolling | reset | 0.173 | 0.271 | 0.556 |

## Occurrence threshold and evaluation window

| index | tol_0.02 | tol_0.03 | tol_0.05 | tol_0.075 | tol_0.1 |
| --- | --- | --- | --- | --- | --- |
| core (rolling/reset) | 0.956 | 0.9 | 0.731 | 0.592 | 0.467 |
| fixed/carried | 0.064 | 0.05 | 0.017 | 0.008 | 0.003 |
| fixed/reset | 0.742 | 0.681 | 0.608 | 0.481 | 0.319 |
| rolling/carried | 0.667 | 0.561 | 0.383 | 0.256 | 0.211 |
| rolling/reset | 0.956 | 0.9 | 0.731 | 0.592 | 0.467 |

The thesis's volume-inconsistency measure (eq. 5-1, periods 2-11) against its
reported distribution:

| index | n | mean | median | min | max | share_gt_6pc | share_gt_10pc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flow-constrained, all 360 cells | 360.0 | 0.1224 | 0.079 | 0.0 | 1.493 | 0.647 | 0.339 |
| thesis-matched subset | 144.0 | 0.082 | 0.068 | 0.0 | 1.489 | 0.611 | 0.146 |
| thesis (178 runs; pp. 92, 124) | 178.0 | 0.09 | 0.072 | 0.017 | 0.292 | 0.6 | 0.27 |

| window | inconsistent | cells | mean_magnitude |
| --- | --- | --- | --- |
| periods 1-15 (paper) | 263 | 360 | 0.1173 |
| periods 2-11 (thesis) | 250 | 360 | 0.1007 |

## Objective-gap diagnostic (core institution)

| group | discount_rate | infeasible | optimal | suboptimal |
| --- | --- | --- | --- | --- |
| NHF | 0.0 | 0.099 | 0.425 | 0.476 |
| NHF | 0.02 | 0.0 | 0.667 | 0.333 |
| NHF | 0.04 | 0.0 | 1.0 | 0.0 |
| NHF | 0.06 | 0.0 | 1.0 | 0.0 |
| flow-constrained | 0.0 | 0.102 | 0.225 | 0.673 |
| flow-constrained | 0.02 | 0.176 | 0.364 | 0.46 |
| flow-constrained | 0.04 | 0.203 | 0.249 | 0.548 |
| flow-constrained | 0.06 | 0.211 | 0.244 | 0.544 |

First non-optimal period per cell (gap as % of the subproblem NPV):

| index | cells_with_a_deviation | first_is_infeasible | first_suboptimal_median_gap_pc_npv | first_suboptimal_p90_gap_pc_npv | first_period_median |
| --- | --- | --- | --- | --- | --- |
| NHF | 28.0 | 0.0 | 0.0293 | 1.7074 | 3.0 |
| flow-constrained | 358.0 | 23.0 | 0.1476 | 3.0604 | 3.0 |

| group | rule | inconsistent | cells |
| --- | --- | --- | --- |
| flow-constrained | metric: mean divergence > 5% | 263 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 1e-06 of NPV | 358 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.0001 of NPV | 358 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.001 of NPV | 358 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.01 of NPV | 348 | 360 |
| NHF | metric: mean divergence > 5% | 27 | 72 |
| NHF | gap: any period infeasible or gap >= 1e-06 of NPV | 28 | 72 |
| NHF | gap: any period infeasible or gap >= 0.0001 of NPV | 28 | 72 |
| NHF | gap: any period infeasible or gap >= 0.001 of NPV | 28 | 72 |
| NHF | gap: any period infeasible or gap >= 0.01 of NPV | 27 | 72 |

## Descriptives

Paired landbases with/without the negatively valued CM-CE ecoclass:

| grid | with_cmce | without_cmce | with_magnitude | without_magnitude |
| --- | --- | --- | --- | --- |
| core (volume) | 77/80 | 51/80 | 0.1466 | 0.1315 |
| E3 volume | 77/80 | 51/80 | 0.1466 | 0.1315 |
| E3 revenue | 58/80 | 56/80 | 0.1322 | 0.1619 |

By discount rate (flow-constrained):

| discount_rate | inconsistent | cells | occurrence | mean_magnitude |
| --- | --- | --- | --- | --- |
| 0.0 | 90.0 | 90.0 | 1.0 | 0.2156 |
| 0.02 | 42.0 | 90.0 | 0.4667 | 0.067 |
| 0.04 | 54.0 | 90.0 | 0.6 | 0.0769 |
| 0.06 | 77.0 | 90.0 | 0.8556 | 0.1096 |

E2 calibrated cap vs the *realized* NDY path (median relative difference):

| discount_rate | volume_cap_vs_realized_ndy | volume_cap_vs_announced_ndy | npv_cap_vs_realized_ndy |
| --- | --- | --- | --- |
| 0.0 | 0.1013 | -0.1227 | 0.1031 |
| 0.02 | -0.0041 | -0.1054 | -0.0315 |
| 0.04 | -0.0107 | -0.1175 | -0.0608 |
| 0.06 | 0.0021 | -0.1102 | -0.0674 |
| all (median) | -0.0046 | -0.1148 | -0.0462 |

## Random landbases: seed sensitivity

| landbase_seed | inconsistent | cells | occurrence | mean_magnitude |
| --- | --- | --- | --- | --- |
| 42.0 | 109.0 | 160.0 | 0.6812 | 0.0994 |
| 1042.0 | 119.0 | 160.0 | 0.7438 | 0.1032 |
| 2042.0 | 116.0 | 160.0 | 0.725 | 0.1013 |
| 3042.0 | 113.0 | 160.0 | 0.7062 | 0.0983 |
| 4042.0 | 126.0 | 160.0 | 0.7875 | 0.1054 |
