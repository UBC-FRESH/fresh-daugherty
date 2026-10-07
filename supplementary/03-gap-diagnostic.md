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
| +/-10% | 0.127 | 0.365 | 0.508 |
| +/-20% | 0.152 | 0.263 | 0.585 |
| -10% | 0.116 | 0.469 | 0.415 |
| -20% | 0.11 | 0.448 | 0.441 |
| NDY | 0.692 | 0.111 | 0.196 |
| NHF | 0.072 | 0.724 | 0.203 |

## By discount rate

| discount_rate | infeasible | optimal | suboptimal |
| --- | --- | --- | --- |
| 0.0 | 0.136 | 0.155 | 0.709 |
| 0.02 | 0.259 | 0.377 | 0.364 |
| 0.04 | 0.214 | 0.535 | 0.251 |
| 0.06 | 0.237 | 0.521 | 0.242 |

Reading: under flow-constrained policies the announced tail is predominantly
**suboptimal** (strictly improvable) or **infeasible** (cannot even be
implemented) from the realized state — genuine inconsistency. Under NHF the
announced tail stays optimal where the control is consistent; where the control
diverges (0%: 18/18, 2%: 16/18, 4%: 0/18, 6%: 0/18), the deviations are material
(34/72 NHF scenarios with a gap of at least 1% of the
optimum, or infeasible) and mostly disappear under a fixed horizon
(0/72): a rolling-horizon effect rather than tie-breaking.
