# 10 — Review analyses (P15)

Analyses added in response to a pre-submission review (fresh-daugherty P15,
issue #82). Every table regenerates from the tracked records via the
`scripts/analyze_p15_*.py` scripts (re-run by this builder). Records:
[institution grid](../results/experiments/grid_institutions.csv) /
[seed grid](../results/experiments/grid_seeds.csv); core, E2-E4 records as in
pages 02 and 06-08.

## Headline basis: the thesis's observation window (P17)

Since P17 (#101) the paper's headline basis is the thesis's observation window,
periods 2-11 (thesis p. 83), because without the thesis's terminal constraints
end-of-horizon effects inflate the full-horizon metric; periods 1-15 are kept as
a sensitivity. Both bases side by side (`scripts/analyze_p17_headline.py`):

| group | n | inconsistent_2-11 | occurrence_2-11 | magnitude_2-11 | inconsistent_1-15 | occurrence_1-15 | magnitude_1-15 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NHF | 72 | 19 | 0.264 | 0.1323 | 28 | 0.389 | 0.1372 |
| flow-constrained | 360 | 187 | 0.519 | 0.0783 | 239 | 0.664 | 0.1006 |

| group | discount_rate | n | inconsistent_2-11 | occurrence_2-11 | magnitude_2-11 | inconsistent_1-15 | occurrence_1-15 | magnitude_1-15 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NHF | 0.0 | 18 | 18 | 1.0 | 0.507 | 18 | 1.0 | 0.5048 |
| NHF | 0.02 | 18 | 1 | 0.056 | 0.0222 | 10 | 0.556 | 0.0441 |
| NHF | 0.04 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| NHF | 0.06 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| flow-constrained | 0.0 | 90 | 89 | 0.989 | 0.174 | 90 | 1.0 | 0.2113 |
| flow-constrained | 0.02 | 90 | 26 | 0.289 | 0.0414 | 54 | 0.6 | 0.0638 |
| flow-constrained | 0.04 | 90 | 37 | 0.411 | 0.0448 | 46 | 0.511 | 0.0568 |
| flow-constrained | 0.06 | 90 | 35 | 0.389 | 0.0532 | 49 | 0.544 | 0.0706 |

| horizon_institution | flow_history | group | n | inconsistent_2-11 | occurrence_2-11 | magnitude_2-11 | inconsistent_1-15 | occurrence_1-15 | magnitude_1-15 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed | carried | NHF | 72 | 0 | 0.0 | 0.0 | 2 | 0.028 | 0.0021 |
| fixed | carried | flow-constrained | 360 | 0 | 0.0 | 0.0 | 4 | 0.011 | 0.0017 |
| fixed | reset | NHF | 72 | 0 | 0.0 | 0.0 | 2 | 0.028 | 0.0021 |
| fixed | reset | flow-constrained | 360 | 137 | 0.381 | 0.0629 | 143 | 0.397 | 0.0757 |
| rolling | carried | NHF | 72 | 19 | 0.264 | 0.1323 | 28 | 0.389 | 0.1372 |
| rolling | carried | flow-constrained | 360 | 87 | 0.242 | 0.0423 | 124 | 0.344 | 0.0658 |
| rolling | reset | NHF | 72 | 19 | 0.264 | 0.1323 | 28 | 0.389 | 0.1372 |
| rolling | reset | flow-constrained | 360 | 187 | 0.519 | 0.0783 | 239 | 0.664 | 0.1006 |

## Comparison with the thesis on matched populations

The thesis's volume inconsistency (eq. 5-1, periods 2-11) on full-choice
equivalents of its combination sets vs its Table 6.2 (p. 99), its
carried-history test (pp. 118-120) and its per-landbase reference run (NDY, 4%,
p. 124) (`scripts/analyze_p17_thesis_comparison.py`):

| subset | n | mean | median | thesis_n | thesis_mean | thesis_median |
| --- | --- | --- | --- | --- | --- | --- |
| landbases 1-6 (over-mature) | 54 | 0.0727 | 0.0537 | 90 | 0.1185 | 0.096 |
| landbases 7-10 (young growth) | 36 | 0.0456 | 0.0494 | 48 | 0.0684 | 0.066 |
| landbases 11-18 (random) | 40 | 0.0451 | 0.0487 | 40 | 0.053 | 0.052 |
| all | 130 | 0.0567 | 0.0498 | 178 | 0.0902 | 0.0715 |

| horizon_institution | flow_history | size | mean | median | thesis_mean |
| --- | --- | --- | --- | --- | --- |
| fixed | carried | 50 | 0.0 | 0.0 | nan |
| fixed | reset | 50 | 0.0633 | 0.0511 | nan |
| rolling | carried | 50 | 0.0076 | 0.0005 | 0.019 |
| rolling | reset | 50 | 0.068 | 0.0583 | nan |

| landbase | thesis_volume_inconsistency_2_11 | mean_abs_rel_deviation_2_11 | thesis_p124 |
| --- | --- | --- | --- |
| 1 | 0.0681 | 0.0681 | >5% |
| 2 | 0.0523 | 0.0523 | >5% |
| 3 | 0.0944 | 0.1011 | >5% |
| 4 | 0.0 | 0.0 | >5% |
| 5 | 0.0496 | 0.0412 | >5% |
| 6 | 0.0028 | 0.0025 | >5% |
| 7 | 0.0879 | 0.0867 | >5% |
| 8 | 0.0106 | 0.0102 | >5% |
| 9 | 0.0594 | 0.0594 | <3% |
| 10 | 0.0655 | 0.0655 | >5% |
| 11 | 0.0562 | 0.0562 | <3% |
| 12 | 0.0496 | 0.0496 | <3% |
| 13 | 0.049 | 0.049 | <3% |
| 14 | 0.0509 | 0.0509 | <3% |
| 15 | 0.0474 | 0.0474 | <3% |
| 16 | 0.0502 | 0.0502 | <3% |
| 17 | 0.0638 | 0.0638 | <3% |
| 18 | 0.0552 | 0.0552 | <3% |

## Replanning institution (full horizon, periods 1-15)

Flow-constrained occurrence: rolling horizon + reset flow history (the core
grid) 239/360 (66%); fixed horizon + reset 143/360 (40%);
rolling + carried 124/360 (34%); fixed horizon + carried history
(each replan solves the exact tail of the original problem)
4/360 (1%). A null test (CI) confirms that fixed + carried
replanning from the plan's own state reproduces the plan.

| horizon_institution | flow_history | inconsistent | cells | occurrence | mean_magnitude | relax_share |
| --- | --- | --- | --- | --- | --- | --- |
| fixed | carried | 4 | 360 | 0.0111 | 0.0017 | 0.0 |
| fixed | reset | 143 | 360 | 0.3972 | 0.0757 | 0.0 |
| rolling | carried | 124 | 360 | 0.3444 | 0.0658 | 0.0988 |
| rolling | reset | 239 | 360 | 0.6639 | 0.1006 | 0.0 |

NHF control by institution:

| horizon_institution | flow_history | inconsistent | cells | mean_magnitude |
| --- | --- | --- | --- | --- |
| fixed | carried | 2 | 72 | 0.0021 |
| fixed | reset | 2 | 72 | 0.0021 |
| rolling | carried | 28 | 72 | 0.1372 |
| rolling | reset | 28 | 72 | 0.1372 |

Gap-diagnostic tail status by institution (flow-constrained, periods > 1):

| horizon_institution | flow_history | infeasible | optimal | suboptimal |
| --- | --- | --- | --- | --- |
| fixed | carried | 0.0 | 0.997 | 0.003 |
| fixed | reset | 0.115 | 0.568 | 0.317 |
| rolling | carried | 0.344 | 0.557 | 0.099 |
| rolling | reset | 0.263 | 0.368 | 0.369 |

## Occurrence threshold and evaluation window

| index | tol_0.02 | tol_0.03 | tol_0.05 | tol_0.075 | tol_0.1 |
| --- | --- | --- | --- | --- | --- |
| core (rolling/reset) | 0.872 | 0.767 | 0.664 | 0.461 | 0.397 |
| fixed/carried | 0.036 | 0.031 | 0.011 | 0.0 | 0.0 |
| fixed/reset | 0.589 | 0.497 | 0.397 | 0.319 | 0.264 |
| rolling/carried | 0.642 | 0.544 | 0.344 | 0.244 | 0.214 |
| rolling/reset | 0.872 | 0.767 | 0.664 | 0.461 | 0.397 |

The thesis's volume-inconsistency measure (eq. 5-1, periods 2-11) against its
reported distribution:

| index | n | mean | median | min | max | share_gt_6pc | share_gt_10pc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flow-constrained, all 360 cells | 360.0 | 0.0888 | 0.055 | 0.0 | 0.7703 | 0.464 | 0.297 |
| thesis-matched subset | 144.0 | 0.0552 | 0.0501 | 0.0 | 0.333 | 0.347 | 0.132 |
| thesis (178 runs; pp. 92, 124) | 178.0 | 0.09 | 0.072 | 0.017 | 0.292 | 0.6 | 0.27 |

| window | inconsistent | cells | mean_magnitude |
| --- | --- | --- | --- |
| periods 1-15 (paper) | 239 | 360 | 0.1006 |
| periods 2-11 (thesis) | 187 | 360 | 0.0783 |

## Objective-gap diagnostic (core institution)

| group | discount_rate | infeasible | optimal | suboptimal |
| --- | --- | --- | --- | --- |
| NHF | 0.0 | 0.099 | 0.377 | 0.524 |
| NHF | 0.02 | 0.151 | 0.655 | 0.194 |
| NHF | 0.04 | 0.0 | 1.0 | 0.0 |
| NHF | 0.06 | 0.0 | 1.0 | 0.0 |
| flow-constrained | 0.0 | 0.117 | 0.211 | 0.672 |
| flow-constrained | 0.02 | 0.323 | 0.363 | 0.314 |
| flow-constrained | 0.04 | 0.295 | 0.463 | 0.241 |
| flow-constrained | 0.06 | 0.318 | 0.434 | 0.248 |

First non-optimal period per cell (gap as % of the subproblem NPV):

| index | cells_with_a_deviation | first_is_infeasible | first_suboptimal_median_gap_pc_npv | first_suboptimal_p90_gap_pc_npv | first_period_median |
| --- | --- | --- | --- | --- | --- |
| NHF | 28.0 | 0.0 | 0.0298 | 2.2146 | 3.0 |
| flow-constrained | 358.0 | 83.0 | 0.0892 | 3.6406 | 5.0 |

| group | rule | inconsistent | cells |
| --- | --- | --- | --- |
| flow-constrained | metric: mean divergence > 5% | 239 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 1e-06 of NPV | 358 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.0001 of NPV | 358 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.001 of NPV | 358 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.01 of NPV | 355 | 360 |
| NHF | metric: mean divergence > 5% | 28 | 72 |
| NHF | gap: any period infeasible or gap >= 1e-06 of NPV | 28 | 72 |
| NHF | gap: any period infeasible or gap >= 0.0001 of NPV | 28 | 72 |
| NHF | gap: any period infeasible or gap >= 0.001 of NPV | 28 | 72 |
| NHF | gap: any period infeasible or gap >= 0.01 of NPV | 28 | 72 |

## Descriptives

Paired landbases with/without the negatively valued CM-CE ecoclass:

| grid | with_cmce | without_cmce | with_magnitude | without_magnitude |
| --- | --- | --- | --- | --- |
| core (volume) | 79/80 | 51/80 | 0.1411 | 0.1111 |
| E3 volume | 79/80 | 51/80 | 0.1411 | 0.1111 |
| E3 revenue | 53/80 | 50/80 | 0.123 | 0.1254 |

By discount rate (flow-constrained):

| discount_rate | inconsistent | cells | occurrence | mean_magnitude |
| --- | --- | --- | --- | --- |
| 0.0 | 90.0 | 90.0 | 1.0 | 0.2113 |
| 0.02 | 54.0 | 90.0 | 0.6 | 0.0638 |
| 0.04 | 46.0 | 90.0 | 0.5111 | 0.0568 |
| 0.06 | 49.0 | 90.0 | 0.5444 | 0.0706 |

E2 calibrated cap vs the *realized* NDY path (median relative difference):

| discount_rate | volume_cap_vs_realized_ndy | volume_cap_vs_announced_ndy | npv_cap_vs_realized_ndy |
| --- | --- | --- | --- |
| 0.0 | 0.0768 | -0.1254 | 0.0804 |
| 0.02 | 0.0129 | -0.0483 | 0.0043 |
| 0.04 | 0.0158 | -0.0496 | -0.0067 |
| 0.06 | 0.0248 | -0.0343 | -0.0073 |
| all (median) | 0.017 | -0.0953 | -0.0036 |

## Random landbases: seed sensitivity

| landbase_seed | inconsistent | cells | occurrence | mean_magnitude |
| --- | --- | --- | --- | --- |
| 42.0 | 82.0 | 160.0 | 0.5125 | 0.0787 |
| 1042.0 | 81.0 | 160.0 | 0.5062 | 0.0819 |
| 2042.0 | 75.0 | 160.0 | 0.4688 | 0.0803 |
| 3042.0 | 84.0 | 160.0 | 0.525 | 0.0785 |
| 4042.0 | 90.0 | 160.0 | 0.5625 | 0.0853 |
