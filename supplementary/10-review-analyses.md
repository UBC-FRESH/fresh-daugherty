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
| NHF | 72 | 34 | 0.472 | 0.1675 | 34 | 0.472 | 0.1712 |
| flow-constrained | 360 | 178 | 0.494 | 0.0719 | 203 | 0.564 | 0.0878 |

| group | discount_rate | n | inconsistent_2-11 | occurrence_2-11 | magnitude_2-11 | inconsistent_1-15 | occurrence_1-15 | magnitude_1-15 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NHF | 0.0 | 18 | 18 | 1.0 | 0.4916 | 18 | 1.0 | 0.5154 |
| NHF | 0.02 | 18 | 16 | 0.889 | 0.1785 | 16 | 0.889 | 0.1693 |
| NHF | 0.04 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| NHF | 0.06 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| flow-constrained | 0.0 | 90 | 90 | 1.0 | 0.1611 | 90 | 1.0 | 0.192 |
| flow-constrained | 0.02 | 90 | 26 | 0.289 | 0.0434 | 43 | 0.478 | 0.0536 |
| flow-constrained | 0.04 | 90 | 28 | 0.311 | 0.0378 | 32 | 0.356 | 0.0476 |
| flow-constrained | 0.06 | 90 | 34 | 0.378 | 0.0453 | 38 | 0.422 | 0.0581 |

| horizon_institution | flow_history | group | n | inconsistent_2-11 | occurrence_2-11 | magnitude_2-11 | inconsistent_1-15 | occurrence_1-15 | magnitude_1-15 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed | carried | NHF | 72 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | carried | flow-constrained | 360 | 1 | 0.003 | 0.0003 | 0 | 0.0 | 0.0002 |
| fixed | reset | NHF | 72 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | reset | flow-constrained | 360 | 98 | 0.272 | 0.0461 | 88 | 0.244 | 0.0419 |
| rolling | carried | NHF | 72 | 34 | 0.472 | 0.1675 | 34 | 0.472 | 0.1712 |
| rolling | carried | flow-constrained | 360 | 87 | 0.242 | 0.0349 | 118 | 0.328 | 0.054 |
| rolling | reset | NHF | 72 | 34 | 0.472 | 0.1675 | 34 | 0.472 | 0.1712 |
| rolling | reset | flow-constrained | 360 | 178 | 0.494 | 0.0719 | 203 | 0.564 | 0.0878 |

## Comparison with the thesis on matched populations

The thesis's volume inconsistency (eq. 5-1, periods 2-11) on full-choice
equivalents of its combination sets vs its Table 6.2 (p. 99), its
carried-history test (pp. 118-120) and its per-landbase reference run (NDY, 4%,
p. 124) (`scripts/analyze_p17_thesis_comparison.py`):

| subset | n | mean | median | thesis_n | thesis_mean | thesis_median |
| --- | --- | --- | --- | --- | --- | --- |
| landbases 1-6 (over-mature) | 54 | 0.0782 | 0.0763 | 90 | 0.1185 | 0.096 |
| landbases 7-10 (young growth) | 36 | 0.0343 | 0.0165 | 48 | 0.0684 | 0.066 |
| landbases 11-18 (random) | 40 | 0.0366 | 0.0442 | 40 | 0.053 | 0.052 |
| all | 130 | 0.0532 | 0.0442 | 178 | 0.0902 | 0.0715 |

| horizon_institution | flow_history | size | mean | median | thesis_mean |
| --- | --- | --- | --- | --- | --- |
| fixed | carried | 50 | 0.0 | 0.0 | nan |
| fixed | reset | 50 | 0.0474 | 0.0145 | nan |
| rolling | carried | 50 | 0.0055 | 0.0003 | 0.019 |
| rolling | reset | 50 | 0.0524 | 0.0333 | nan |

| landbase | thesis_volume_inconsistency_2_11 | mean_abs_rel_deviation_2_11 | thesis_p124 |
| --- | --- | --- | --- |
| 1 | 0.0954 | 0.0954 | >5% |
| 2 | 0.0732 | 0.0732 | >5% |
| 3 | 0.0876 | 0.0876 | >5% |
| 4 | 0.0246 | 0.0246 | >5% |
| 5 | 0.0826 | 0.0872 | >5% |
| 6 | 0.0035 | 0.0035 | >5% |
| 7 | 0.0638 | 0.0637 | >5% |
| 8 | 0.0 | 0.0 | >5% |
| 9 | 0.0547 | 0.0547 | <3% |
| 10 | 0.0539 | 0.0539 | >5% |
| 11 | 0.0494 | 0.0494 | <3% |
| 12 | 0.0509 | 0.0509 | <3% |
| 13 | 0.0513 | 0.0513 | <3% |
| 14 | 0.0507 | 0.0507 | <3% |
| 15 | 0.0506 | 0.0506 | <3% |
| 16 | 0.0565 | 0.0565 | <3% |
| 17 | 0.0675 | 0.0675 | <3% |
| 18 | 0.0564 | 0.0564 | <3% |

By harvest-flow policy on the thesis's Table 6.8 populations (p. 111; 4%, full
choices; bounded decline on landbases 1-10 only):

| policy | n | mean | median | thesis_mean | thesis_median |
| --- | --- | --- | --- | --- | --- |
| NDY | 18 | 0.054 | 0.0543 | 0.06 | 0.034 |
| -10% | 10 | 0.0264 | 0.002 | 0.157 | 0.192 |
| -20% | 10 | 0.0235 | 0.0055 | 0.161 | 0.169 |
| +/-10% | 18 | 0.036 | 0.0083 | 0.071 | 0.046 |
| +/-20% | 18 | 0.0631 | 0.0377 | 0.082 | 0.064 |

Institutions by discount rate (both bases):

| horizon_institution | flow_history | group | discount_rate | n | inconsistent_2-11 | occurrence_2-11 | magnitude_2-11 | inconsistent_1-15 | occurrence_1-15 | magnitude_1-15 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed | carried | NHF | 0.0 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | carried | NHF | 0.02 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | carried | NHF | 0.04 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | carried | NHF | 0.06 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | carried | flow-constrained | 0.0 | 90 | 1 | 0.011 | 0.001 | 0 | 0.0 | 0.0007 |
| fixed | carried | flow-constrained | 0.02 | 90 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | carried | flow-constrained | 0.04 | 90 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | carried | flow-constrained | 0.06 | 90 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0001 |
| fixed | reset | NHF | 0.0 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | reset | NHF | 0.02 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | reset | NHF | 0.04 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | reset | NHF | 0.06 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| fixed | reset | flow-constrained | 0.0 | 90 | 40 | 0.444 | 0.0863 | 28 | 0.311 | 0.0586 |
| fixed | reset | flow-constrained | 0.02 | 90 | 17 | 0.189 | 0.0285 | 15 | 0.167 | 0.0252 |
| fixed | reset | flow-constrained | 0.04 | 90 | 18 | 0.2 | 0.0299 | 20 | 0.222 | 0.0331 |
| fixed | reset | flow-constrained | 0.06 | 90 | 23 | 0.256 | 0.0398 | 25 | 0.278 | 0.0508 |
| rolling | carried | NHF | 0.0 | 18 | 18 | 1.0 | 0.4916 | 18 | 1.0 | 0.5154 |
| rolling | carried | NHF | 0.02 | 18 | 16 | 0.889 | 0.1785 | 16 | 0.889 | 0.1693 |
| rolling | carried | NHF | 0.04 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| rolling | carried | NHF | 0.06 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| rolling | carried | flow-constrained | 0.0 | 90 | 81 | 0.9 | 0.1067 | 89 | 0.989 | 0.153 |
| rolling | carried | flow-constrained | 0.02 | 90 | 4 | 0.044 | 0.0182 | 19 | 0.211 | 0.0337 |
| rolling | carried | flow-constrained | 0.04 | 90 | 1 | 0.011 | 0.0089 | 7 | 0.078 | 0.0183 |
| rolling | carried | flow-constrained | 0.06 | 90 | 1 | 0.011 | 0.0059 | 3 | 0.033 | 0.011 |
| rolling | reset | NHF | 0.0 | 18 | 18 | 1.0 | 0.4916 | 18 | 1.0 | 0.5154 |
| rolling | reset | NHF | 0.02 | 18 | 16 | 0.889 | 0.1785 | 16 | 0.889 | 0.1693 |
| rolling | reset | NHF | 0.04 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| rolling | reset | NHF | 0.06 | 18 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| rolling | reset | flow-constrained | 0.0 | 90 | 90 | 1.0 | 0.1611 | 90 | 1.0 | 0.192 |
| rolling | reset | flow-constrained | 0.02 | 90 | 26 | 0.289 | 0.0434 | 43 | 0.478 | 0.0536 |
| rolling | reset | flow-constrained | 0.04 | 90 | 28 | 0.311 | 0.0378 | 32 | 0.356 | 0.0476 |
| rolling | reset | flow-constrained | 0.06 | 90 | 34 | 0.378 | 0.0453 | 38 | 0.422 | 0.0581 |

## Replanning institution (full horizon, periods 1-15)

Flow-constrained occurrence: rolling horizon + reset flow history (the core
grid) 203/360 (56%); fixed horizon + reset 88/360 (24%);
rolling + carried 118/360 (33%); fixed horizon + carried history
(each replan solves the exact tail of the original problem)
0/360 (0%). A null test (CI) confirms that fixed + carried
replanning from the plan's own state reproduces the plan.

| horizon_institution | flow_history | inconsistent | cells | occurrence | mean_magnitude | relax_share |
| --- | --- | --- | --- | --- | --- | --- |
| fixed | carried | 0 | 360 | 0.0 | 0.0002 | 0.0 |
| fixed | reset | 88 | 360 | 0.2444 | 0.0419 | 0.0 |
| rolling | carried | 118 | 360 | 0.3278 | 0.054 | 0.1365 |
| rolling | reset | 203 | 360 | 0.5639 | 0.0878 | 0.0 |

NHF control by institution:

| horizon_institution | flow_history | inconsistent | cells | mean_magnitude |
| --- | --- | --- | --- | --- |
| fixed | carried | 0 | 72 | 0.0 |
| fixed | reset | 0 | 72 | 0.0 |
| rolling | carried | 34 | 72 | 0.1712 |
| rolling | reset | 34 | 72 | 0.1712 |

Gap-diagnostic tail status by institution (flow-constrained, periods > 1):

| horizon_institution | flow_history | infeasible | optimal | suboptimal |
| --- | --- | --- | --- | --- |
| fixed | carried | 0.001 | 0.998 | 0.001 |
| fixed | reset | 0.102 | 0.587 | 0.311 |
| rolling | carried | 0.317 | 0.552 | 0.131 |
| rolling | reset | 0.239 | 0.331 | 0.429 |

## Occurrence threshold and evaluation window

| index | tol_0.02 | tol_0.03 | tol_0.05 | tol_0.075 | tol_0.1 |
| --- | --- | --- | --- | --- | --- |
| core (rolling/reset) | 0.822 | 0.711 | 0.564 | 0.417 | 0.358 |
| fixed/carried | 0.003 | 0.003 | 0.0 | 0.0 | 0.0 |
| fixed/reset | 0.497 | 0.367 | 0.244 | 0.169 | 0.131 |
| rolling/carried | 0.544 | 0.453 | 0.328 | 0.242 | 0.214 |
| rolling/reset | 0.822 | 0.711 | 0.564 | 0.417 | 0.358 |

| window | inconsistent | cells | mean_magnitude |
| --- | --- | --- | --- |
| periods 1-15 (paper) | 203 | 360 | 0.0878 |
| periods 2-11 (thesis) | 178 | 360 | 0.0719 |

## Objective-gap diagnostic (core institution)

| group | discount_rate | infeasible | optimal | suboptimal |
| --- | --- | --- | --- | --- |
| NHF | 0.0 | 0.071 | 0.429 | 0.5 |
| NHF | 0.02 | 0.218 | 0.468 | 0.313 |
| NHF | 0.04 | 0.0 | 1.0 | 0.0 |
| NHF | 0.06 | 0.0 | 1.0 | 0.0 |
| flow-constrained | 0.0 | 0.149 | 0.1 | 0.751 |
| flow-constrained | 0.02 | 0.267 | 0.359 | 0.375 |
| flow-constrained | 0.04 | 0.257 | 0.442 | 0.301 |
| flow-constrained | 0.06 | 0.285 | 0.425 | 0.29 |

First non-optimal period per cell (gap as % of the subproblem NPV):

| index | cells_with_a_deviation | first_is_infeasible | first_suboptimal_median_gap_pc_npv | first_suboptimal_p90_gap_pc_npv | first_period_median |
| --- | --- | --- | --- | --- | --- |
| NHF | 34.0 | 0.0 | 0.0499 | 0.6169 | 2.0 |
| flow-constrained | 357.0 | 53.0 | 0.056 | 1.2502 | 4.0 |

| group | rule | inconsistent | cells |
| --- | --- | --- | --- |
| flow-constrained | metric: mean divergence > 5% | 203 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 1e-06 of NPV | 357 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.0001 of NPV | 357 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.001 of NPV | 354 | 360 |
| flow-constrained | gap: any period infeasible or gap >= 0.01 of NPV | 332 | 360 |
| NHF | metric: mean divergence > 5% | 34 | 72 |
| NHF | gap: any period infeasible or gap >= 1e-06 of NPV | 34 | 72 |
| NHF | gap: any period infeasible or gap >= 0.0001 of NPV | 34 | 72 |
| NHF | gap: any period infeasible or gap >= 0.001 of NPV | 34 | 72 |
| NHF | gap: any period infeasible or gap >= 0.01 of NPV | 34 | 72 |

## Descriptives

Paired landbases with/without the negatively valued CM-CE ecoclass:

| grid | with_cmce | without_cmce | with_magnitude | without_magnitude |
| --- | --- | --- | --- | --- |
| core (volume) | 72/80 | 38/80 | 0.1357 | 0.0895 |
| E3 volume | 72/80 | 38/80 | 0.1357 | 0.0895 |
| E3 revenue | 53/80 | 45/80 | 0.1296 | 0.1109 |

By discount rate (flow-constrained):

| discount_rate | inconsistent | cells | occurrence | mean_magnitude |
| --- | --- | --- | --- | --- |
| 0.0 | 90.0 | 90.0 | 1.0 | 0.192 |
| 0.02 | 43.0 | 90.0 | 0.4778 | 0.0536 |
| 0.04 | 32.0 | 90.0 | 0.3556 | 0.0476 |
| 0.06 | 38.0 | 90.0 | 0.4222 | 0.0581 |

E2 calibrated cap vs the *realized* NDY path (median relative difference):

| discount_rate | volume_cap_vs_realized_ndy | volume_cap_vs_announced_ndy | npv_cap_vs_realized_ndy |
| --- | --- | --- | --- |
| 0.0 | 0.0631 | -0.0853 | 0.0456 |
| 0.02 | 0.0544 | -0.0049 | 0.0337 |
| 0.04 | 0.011 | -0.0507 | -0.0189 |
| 0.06 | 0.0162 | -0.0436 | -0.0203 |
| all (median) | 0.0233 | -0.0523 | -0.0058 |

## Random landbases: seed sensitivity

| landbase_seed | inconsistent | cells | occurrence | mean_magnitude |
| --- | --- | --- | --- | --- |
| 42.0 | 72.0 | 160.0 | 0.45 | 0.0686 |
| 1042.0 | 75.0 | 160.0 | 0.4688 | 0.0701 |
| 2042.0 | 74.0 | 160.0 | 0.4625 | 0.07 |
| 3042.0 | 78.0 | 160.0 | 0.4875 | 0.0698 |
| 4042.0 | 76.0 | 160.0 | 0.475 | 0.0721 |
