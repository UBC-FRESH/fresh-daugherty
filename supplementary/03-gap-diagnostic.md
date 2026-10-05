# 03 — Objective-gap diagnostic evidence

The gap diagnostic rules out the alternate-optima reading of the divergence:
at each replan the subproblem is solved freely and again with the period-1
harvest held to the announced plan's value; if the free objective strictly
exceeds the tail-fixed objective — or the announced value is infeasible from
the realized state — the announced tail is genuinely dynamically
inconsistent.

The full-grid gap records are the volume-denominated cells of the E3 grid
([grid_value_flow_gaps.csv](../results/experiments/grid_value_flow_gaps.csv),
`flow_denominator == 'volume'`; identical policies/rates/landbases as the
core grid). Shares of replan periods (period > 1) by tail status:

## By harvest-flow policy

| flow_policy | infeasible | optimal | suboptimal |
| --- | --- | --- | --- |
| +/-10% | 0.27 | 0.335 | 0.395 |
| +/-20% | 0.239 | 0.286 | 0.475 |
| -10% | 0.139 | 0.549 | 0.312 |
| -20% | 0.13 | 0.56 | 0.311 |
| NDY | 0.511 | 0.15 | 0.339 |
| NHF | 0.059 | 0.766 | 0.176 |

## By discount rate

| discount_rate | infeasible | optimal | suboptimal |
| --- | --- | --- | --- |
| 0.0 | 0.107 | 0.256 | 0.637 |
| 0.02 | 0.288 | 0.423 | 0.289 |
| 0.04 | 0.246 | 0.546 | 0.208 |
| 0.06 | 0.257 | 0.538 | 0.205 |

Reading: under flow-constrained policies the announced tail is predominantly
**suboptimal** (strictly improvable) or **infeasible** (cannot even be
implemented) from the realized state — genuine inconsistency. Under NHF the
announced tail stays optimal where the control is consistent; where the control
diverges (0%: 18/18, 2%: 10/18, 4%: 0/18, 6%: 0/18), the deviations are material
(28/72 NHF scenarios with a gap of at least 1% of the
optimum, or infeasible) and mostly disappear under a fixed horizon
(2/72): a rolling-horizon effect rather than tie-breaking.
