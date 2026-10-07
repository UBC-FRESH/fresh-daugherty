# 10 — Review analyses (P15)

Analyses added in response to a pre-submission review (fresh-daugherty P15,
issue #82). Every table regenerates from the tracked records via the
`scripts/analyze_p15_*.py` scripts (re-run by this builder). Records:
[institution grid](../results/experiments/grid_institutions.csv) /
[seed grid](../results/experiments/grid_seeds.csv); core, E2-E4 records as in
pages 02 and 06-08.

## Headline basis: the thesis's observation window (P17)

Since P17 (#101) the paper's headline basis is the thesis's observation window,
periods 2-11 (thesis p. 83); periods 1-15 are kept as a sensitivity. Since P18
(#110) the thesis's terminal constraints are imposed on every flow-constrained
run; they remove end-of-horizon liquidation, but each replan still has its own
end periods, which carry about half of a scenario's summed divergence. Both
bases side by side (`scripts/analyze_p17_headline.py`):

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
| periods 1-15 (sensitivity) | 203 | 360 | 0.0878 |
| periods 2-11 (thesis; paper headline) | 178 | 360 | 0.0719 |

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

Since P19 (#119) these tables are scored over periods 2-11 (the E2
comparison over periods 1-11 and 1-15). Paired landbases with/without the
negatively valued CM-CE ecoclass:

| grid | with_cmce | without_cmce | with_magnitude | without_magnitude |
| --- | --- | --- | --- | --- |
| core (volume) | 67/80 | 37/80 | 0.1259 | 0.081 |
| E3 volume | 67/80 | 37/80 | 0.1259 | 0.081 |
| E3 revenue | 50/80 | 45/80 | 0.1242 | 0.1067 |

By discount rate (flow-constrained):

| discount_rate | inconsistent | cells | occurrence | mean_magnitude |
| --- | --- | --- | --- | --- |
| 0.0 | 90.0 | 90.0 | 1.0 | 0.1611 |
| 0.02 | 26.0 | 90.0 | 0.2889 | 0.0434 |
| 0.04 | 28.0 | 90.0 | 0.3111 | 0.0378 |
| 0.06 | 34.0 | 90.0 | 0.3778 | 0.0453 |

E2 calibrated cap vs the *realized* NDY path (relative difference; medians by
rate, then median, minimum and maximum over the 72 scenarios):

| discount_rate | volume_cap_vs_realized_ndy_1_11 | volume_cap_vs_announced_ndy_1_11 | npv_cap_vs_realized_ndy_1_11 | volume_cap_vs_realized_ndy_1_15 | volume_cap_vs_announced_ndy_1_15 | npv_cap_vs_realized_ndy_1_15 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.0 | 0.0656 | -0.051 | 0.0374 | 0.0631 | -0.0853 | 0.0456 |
| 0.02 | 0.0407 | -0.0013 | 0.0284 | 0.0544 | -0.0049 | 0.0337 |
| 0.04 | -0.0034 | -0.0493 | -0.0196 | 0.011 | -0.0507 | -0.0189 |
| 0.06 | 0.0024 | -0.0431 | -0.0205 | 0.0162 | -0.0436 | -0.0203 |
| all (median) | 0.0136 | -0.0425 | -0.005 | 0.0233 | -0.0523 | -0.0058 |
| all (min) | -0.1479 | -0.2201 | -0.0764 | -0.1555 | -0.2341 | -0.0902 |
| all (max) | 0.3536 | 0.0626 | 0.4419 | 0.1619 | 0.0146 | 0.1802 |

## Random landbases: seed sensitivity

| landbase_seed | inconsistent | cells | occurrence | mean_magnitude |
| --- | --- | --- | --- | --- |
| 42.0 | 72.0 | 160.0 | 0.45 | 0.0686 |
| 1042.0 | 75.0 | 160.0 | 0.4688 | 0.0701 |
| 2042.0 | 74.0 | 160.0 | 0.4625 | 0.07 |
| 3042.0 | 78.0 | 160.0 | 0.4875 | 0.0698 |
| 4042.0 | 76.0 | 160.0 | 0.475 | 0.0721 |

## Final pre-submission audit (P19, periods 2-11)

Tables behind the manuscript numbers added after the final referee audit
(`scripts/analyze_p19_round5.py`).

Replan status (objective-gap diagnostic) by institution; "material_loosening"
is the share of replans whose carried anchor had to be loosened beyond
numerical tolerance:

| institution | policies | replans | optimal | suboptimal | infeasible | material_loosening |
| --- | --- | --- | --- | --- | --- | --- |
| fixed/carried | flow-constrained | 3600 | 0.9989 | 0.0008 | 0.0003 | 0.0 |
| fixed/carried | NHF | 720 | 1.0 | 0.0 | 0.0 | nan |
| fixed/reset | flow-constrained | 3600 | 0.6131 | 0.3222 | 0.0647 | nan |
| fixed/reset | NHF | 720 | 1.0 | 0.0 | 0.0 | nan |
| rolling/carried | flow-constrained | 3600 | 0.6578 | 0.0994 | 0.2428 | 0.1306 |
| rolling/carried | NHF | 720 | 0.7514 | 0.2222 | 0.0264 | nan |
| rolling/reset | flow-constrained | 3600 | 0.4208 | 0.3947 | 0.1844 | nan |
| rolling/reset | NHF | 720 | 0.7514 | 0.2222 | 0.0264 | nan |

Core institution by rate:

| discount_rate | policies | replans | optimal | suboptimal | infeasible |
| --- | --- | --- | --- | --- | --- |
| 0.0 | flow-constrained | 900 | 0.1333 | 0.7456 | 0.1211 |
| 0.0 | NHF | 180 | 0.5056 | 0.4944 | 0.0 |
| 0.02 | flow-constrained | 900 | 0.4611 | 0.3233 | 0.2156 |
| 0.02 | NHF | 180 | 0.5 | 0.3944 | 0.1056 |
| 0.04 | flow-constrained | 900 | 0.55 | 0.2522 | 0.1978 |
| 0.04 | NHF | 180 | 1.0 | 0.0 | 0.0 |
| 0.06 | flow-constrained | 900 | 0.5389 | 0.2578 | 0.2033 |
| 0.06 | NHF | 180 | 1.0 | 0.0 | 0.0 |

Landbase 1, non-optimal replans of ten:

| flow_policy | 0.0 | 0.02 | 0.04 | 0.06 |
| --- | --- | --- | --- | --- |
| NDY | 9 | 10 | 10 | 10 |
| NHF | 1 | 0 | 0 | 0 |

First deviation (flow-constrained, core):

| index | value |
| --- | --- |
| scenarios_with_nonoptimal_replan | 324 |
| first_deviation_infeasible | 40 |
| first_suboptimal_gap_median_pct | 0.051 |
| first_suboptimal_gap_p90_pct | 0.95 |
| inconsistent_with_flag | 178/178 |
| consistent_with_flag | 146/182 |

Extension grids:

| grid | replans | optimal | suboptimal | infeasible |
| --- | --- | --- | --- | --- |
| E2 cap | 720 | 0.9569 | 0.0431 | 0.0 |
| E3 revenue | 3600 | 0.3964 | 0.4944 | 0.1092 |
| E3 volume | 3600 | 0.4208 | 0.3947 | 0.1844 |

| discount_rate | material_loosening | median_loosening_pct | max_loosening_pct | dropped |
| --- | --- | --- | --- | --- |
| 0.0 | 0.4 | nan | nan | nan |
| 0.02 | 0.7194 | nan | nan | nan |
| 0.04 | 0.7389 | nan | nan | nan |
| 0.06 | 0.7361 | nan | nan | nan |
| all | 0.6486 | 1.279 | 2.256 | 0.0 |

Paired CM-CE landbases on all 80 flow-constrained pairs (volume inconsistency,
eq. 5-1, percentage points):

| pair | occurrence_with | occurrence_without | volume_inconsistency_diff_pts | share_higher_with |
| --- | --- | --- | --- | --- |
| 1 vs 2 | 20/20 | 9/20 | 5.76 | 0.9 |
| 3 vs 4 | 17/20 | 9/20 | 7.14 | 0.9 |
| 5 vs 6 | 18/20 | 12/20 | 3.14 | 0.75 |
| 7 vs 8 | 12/20 | 7/20 | 2.79 | 0.8 |
| all 80 pairs | 67/80 | 37/80 | 4.71 | 0.838 |

Exact tail problem (fixed horizon, carried flow history): scenarios whose
realized harvest departs from the announced plan in some period, by size of
the largest departure. These arise from ties among stand-level alternatives of
equal value, which the aggregate harvest-flow diagnostic does not see.

| window | scenarios | max_dev_gt_0.1pct | max_dev_gt_1pct | max_dev_gt_5pct |
| --- | --- | --- | --- | --- |
| periods 2-11 | 360 | 10 | 4 | 2 |
| periods 2-15 | 360 | 14 | 5 | 2 |

| landbase | discount_rate | flow_policy | max_period_deviation |
| --- | --- | --- | --- |
| 1 | 0.06 | +/-10% | 0.0384 |
| 5 | 0.0 | -10% | 0.025 |
| 8 | 0.0 | -10% | 0.4016 |
| 10 | 0.0 | -20% | 0.1299 |
| 15 | 0.06 | +/-20% | 0.0149 |

Occurrence by institution at zero and positive rates:

| horizon_institution | flow_history | 0% | 2-6% |
| --- | --- | --- | --- |
| fixed | carried | 1/90 | 0/270 |
| fixed | reset | 40/90 | 58/270 |
| rolling | carried | 81/90 | 6/270 |
| rolling | reset | 90/90 | 88/270 |

The model's own highest-PNV rotations (FEIS yields, the model's net values,
4%, rotations on the 10-year grid within the thesis's permitted range) vs
Table 5.3, which the terminal targets use:

| ecoclass | prescription | permitted | table_5_3 | model_optimum | model_lev_per_ac |
| --- | --- | --- | --- | --- | --- |
| CH-CW | 2 | 60-150 | 90 | 60 | 449.5 |
| CH-CW | 3 | 100-180 | 100 | 100 | 147.5 |
| CH-CW | 4 | 70-150 | 80 | 70 | 409.7 |
| CH-CW | 5 | 60-150 | 70 | 60 | 555.1 |
| CH-CW | 6 | 70-150 | 90 | 70 | 373.7 |
| CH-CW | 7 | 60-150 | 80 | 60 | 449.5 |
| CD-CP | 2 | 70-150 | 90 | 70 | 230.1 |
| CD-CP | 3 | 120-180 | 120 | 120 | 58.8 |
| CD-CP | 4 | 80-150 | 90 | 80 | 302.7 |
| CD-CP | 5 | 70-150 | 100 | 70 | 397.9 |
| CD-CP | 6 | 80-150 | 110 | 80 | 175.3 |
| CD-CP | 7 | 80-150 | 100 | 80 | 187.3 |
| CR-CF | 1 | 80-150 | 90 | 80 | 210.8 |
| CR-CF | 2 | 80-150 | 100 | 80 | 210.8 |
| CR-CF | 4 | 80-150 | 100 | 80 | 302.2 |
| CR-CF | 6 | 80-150 | 120 | 80 | 210.8 |
| CM-CE | 2 | 110-190 | 150 | 190 | -1.8 |
| CM-CE | 4 | 110-190 | 150 | 190 | -1.7 |
| CM-CE | 6 | 120-200 | 150 | 200 | -1.2 |

Revenue-denominated NDY: the projected plan's volume from one period to the
next (a 1%/yr escalation alone allows about 0.905 per period):

| index | value |
| --- | --- |
| landbase1_4pc_period2_over_period1 | 0.6216 |
| min_ratio_from_positive_harvest | 0.2992 |
| p5_of_cell_minima | 0.6216 |
| median_of_cell_minima | 0.8625 |
| escalation_only_10yr | 0.9053 |

Terminal-rotation sensitivity: the core grid with terminal targets at the
model's own highest-PNV rotations instead of Table 5.3's
([records](../results/experiments/grid_terminal_rotation_model.csv)):

| terminal_rotations | flow_constrained_2_11 | flow_constrained_1_15 | magnitude_2_11 | positive_rates_2_11 | NHF_2_11 | volume_inconsistency_2_11 | occ_0 | occ_0.02 | occ_0.04 | occ_0.06 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Table 5.3 rotations (core) | 178/360 | 203/360 | 0.0719 | 88/270 | 34/72 | 7.61 | 90/90 | 26/90 | 28/90 | 34/90 |
| model-optimal rotations | 161/360 | 212/360 | 0.0768 | 75/270 | 34/72 | 8.12 | 86/90 | 24/90 | 22/90 | 29/90 |

| index | scenarios |
| --- | --- |
| both_inconsistent | 155 |
| core_only | 23 |
| model_only | 6 |
| both_consistent | 176 |
