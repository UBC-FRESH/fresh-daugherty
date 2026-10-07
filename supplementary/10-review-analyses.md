# 10 — Review analyses (P15)

Analyses added in response to a pre-submission review (fresh-daugherty P15,
issue #82). Every table regenerates from the tracked records via the
`scripts/analyze_p15_*.py` scripts (re-run by this builder). Records:
[institution grid](../results/experiments/grid_institutions.csv) /
[seed grid](../results/experiments/grid_seeds.csv); core, E2-E4 records as in
pages 02 and 06-08.

## Replanning institution

Flow-constrained occurrence: rolling horizon + reset flow history (the core
grid) 235/360 (65%); fixed horizon + reset 147/360 (41%);
rolling + carried 118/360 (33%); fixed horizon + carried history
(each replan solves the exact tail of the original problem)
4/360 (1%). A null test (CI) confirms that fixed + carried
replanning from the plan's own state reproduces the plan.

| horizon_institution | flow_history | inconsistent | cells | occurrence | mean_magnitude | relax_share |
| --- | --- | --- | --- | --- | --- | --- |
| fixed | carried | 4 | 360 | 0.0111 | 0.0017 | 0.0 |
| fixed | reset | 147 | 360 | 0.4083 | 0.0763 | 0.0 |
| rolling | carried | 118 | 360 | 0.3278 | 0.0652 | 0.0865 |
| rolling | reset | 235 | 360 | 0.6528 | 0.1014 | 0.0 |

NHF control by institution:

| horizon_institution | flow_history | inconsistent | cells | mean_magnitude |
| --- | --- | --- | --- | --- |
| fixed | carried | 2 | 72 | 0.0021 |
| fixed | reset | 2 | 72 | 0.0021 |
| rolling | carried | 28 | 72 | 0.1297 |
| rolling | reset | 28 | 72 | 0.1297 |

Gap-diagnostic tail status by institution (flow-constrained, periods > 1):

| horizon_institution | flow_history | infeasible | optimal | suboptimal |
| --- | --- | --- | --- | --- |
| fixed | carried | 0.0 | 0.997 | 0.002 |
| fixed | reset | 0.115 | 0.569 | 0.316 |
| rolling | carried | 0.329 | 0.577 | 0.095 |
| rolling | reset | 0.258 | 0.376 | 0.366 |

## Occurrence threshold and evaluation window

| index | tol_0.02 | tol_0.03 | tol_0.05 | tol_0.075 | tol_0.1 |
| --- | --- | --- | --- | --- | --- |
| core (rolling/reset) | 0.881 | 0.775 | 0.653 | 0.447 | 0.386 |
| fixed/carried | 0.036 | 0.031 | 0.011 | 0.0 | 0.0 |
| fixed/reset | 0.603 | 0.514 | 0.408 | 0.303 | 0.264 |
| rolling/carried | 0.642 | 0.531 | 0.328 | 0.242 | 0.206 |
| rolling/reset | 0.881 | 0.775 | 0.653 | 0.447 | 0.386 |

The thesis's volume-inconsistency measure (eq. 5-1, periods 2-11) against its
reported distribution:

| index | n | mean | median | min | max | share_gt_6pc | share_gt_10pc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flow-constrained, all 360 cells | 360.0 | 0.0924 | 0.055 | 0.0 | 0.7703 | 0.469 | 0.297 |
| thesis-matched subset | 144.0 | 0.0582 | 0.0487 | 0.0 | 0.3478 | 0.347 | 0.118 |
| thesis (178 runs; pp. 92, 124) | 178.0 | 0.09 | 0.072 | 0.017 | 0.292 | 0.6 | 0.27 |

| window | inconsistent | cells | mean_magnitude |
| --- | --- | --- | --- |
| periods 1-15 (paper) | 235 | 360 | 0.1014 |
| periods 2-11 (thesis) | 187 | 360 | 0.0797 |

## Objective-gap diagnostic (core institution)

| group | discount_rate | infeasible | optimal | suboptimal |
| --- | --- | --- | --- | --- |
| NHF | 0.0 | 0.083 | 0.409 | 0.508 |
| NHF | 0.02 | 0.151 | 0.655 | 0.194 |
| NHF | 0.04 | 0.0 | 1.0 | 0.0 |
| NHF | 0.06 | 0.0 | 1.0 | 0.0 |
| flow-constrained | 0.0 | 0.112 | 0.225 | 0.663 |
| flow-constrained | 0.02 | 0.315 | 0.377 | 0.308 |
| flow-constrained | 0.04 | 0.295 | 0.456 | 0.249 |
| flow-constrained | 0.06 | 0.309 | 0.445 | 0.246 |

First non-optimal period per cell (gap as % of the subproblem NPV):

| index | cells_with_a_deviation | first_is_infeasible | first_suboptimal_median_gap_pc_npv | first_suboptimal_p90_gap_pc_npv | first_period_median |
| --- | --- | --- | --- | --- | --- |
| NHF | 28.0 | 0.0 | 0.0298 | 1.3069 | 3.0 |
| flow-constrained | 359.0 | 79.0 | 0.0848 | 3.5539 | 5.0 |

| group | rule | inconsistent | cells |
| --- | --- | --- | --- |
| flow-constrained | metric: mean divergence > 5% | 235 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 1e-06 of NPV | 359 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.0001 of NPV | 359 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.001 of NPV | 359 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.01 of NPV | 356 | 360 |
| NHF | metric: mean divergence > 5% | 28 | 72 |
| NHF | gap: any period infeasible or gap >= 1e-06 of NPV | 28 | 72 |
| NHF | gap: any period infeasible or gap >= 0.0001 of NPV | 28 | 72 |
| NHF | gap: any period infeasible or gap >= 0.001 of NPV | 28 | 72 |
| NHF | gap: any period infeasible or gap >= 0.01 of NPV | 28 | 72 |

## Descriptives

Paired landbases with/without the negatively valued CM-CE ecoclass:

| grid | with_cmce | without_cmce | with_magnitude | without_magnitude |
| --- | --- | --- | --- | --- |
| core (volume) | 77/80 | 49/80 | 0.1392 | 0.1163 |
| E3 volume | 77/80 | 49/80 | 0.1392 | 0.1163 |
| E3 revenue | 54/80 | 52/80 | 0.132 | 0.1338 |

By discount rate (flow-constrained):

| discount_rate | inconsistent | cells | occurrence | mean_magnitude |
| --- | --- | --- | --- | --- |
| 0.0 | 90.0 | 90.0 | 1.0 | 0.2141 |
| 0.02 | 52.0 | 90.0 | 0.5778 | 0.0633 |
| 0.04 | 46.0 | 90.0 | 0.5111 | 0.0587 |
| 0.06 | 47.0 | 90.0 | 0.5222 | 0.0693 |

E2 calibrated cap vs the *realized* NDY path (median relative difference):

| discount_rate | volume_cap_vs_realized_ndy | volume_cap_vs_announced_ndy | npv_cap_vs_realized_ndy |
| --- | --- | --- | --- |
| 0.0 | 0.0977 | -0.1237 | 0.0977 |
| 0.02 | 0.0114 | -0.0483 | 0.0037 |
| 0.04 | 0.0158 | -0.0455 | -0.0055 |
| 0.06 | 0.0248 | -0.0343 | -0.0091 |
| all (median) | 0.0165 | -0.0956 | -0.0029 |

## Random landbases: seed sensitivity

| landbase_seed | inconsistent | cells | occurrence | mean_magnitude |
| --- | --- | --- | --- | --- |
| 42.0 | 82.0 | 160.0 | 0.5125 | 0.0787 |
| 1042.0 | 81.0 | 160.0 | 0.5062 | 0.0819 |
| 2042.0 | 75.0 | 160.0 | 0.4688 | 0.0803 |
| 3042.0 | 84.0 | 160.0 | 0.525 | 0.0785 |
| 4042.0 | 90.0 | 160.0 | 0.5625 | 0.0853 |
