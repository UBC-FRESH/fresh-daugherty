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
| +/-10% | 0.255 | 0.329 | 0.416 |
| +/-20% | 0.229 | 0.289 | 0.482 |
| -10% | 0.144 | 0.531 | 0.325 |
| -20% | 0.129 | 0.555 | 0.316 |
| NDY | 0.56 | 0.136 | 0.305 |
| NHF | 0.062 | 0.758 | 0.18 |

## By discount rate

| discount_rate | infeasible | optimal | suboptimal |
| --- | --- | --- | --- |
| 0.0 | 0.114 | 0.239 | 0.647 |
| 0.02 | 0.294 | 0.411 | 0.294 |
| 0.04 | 0.246 | 0.553 | 0.201 |
| 0.06 | 0.265 | 0.528 | 0.206 |

Reading: under flow-constrained policies the announced tail is predominantly
**suboptimal** (strictly improvable) or **infeasible** (cannot even be
implemented) from the realized state — genuine inconsistency. Under NHF the
announced tail stays optimal where the control is consistent; where the control
diverges (0%: 18/18, 2%: 10/18, 4%: 0/18, 6%: 0/18), the deviations are material
(28/72 NHF scenarios with a gap of at least 1% of the
optimum, or infeasible) and mostly disappear under a fixed horizon
(2/72): a rolling-horizon effect rather than tie-breaking.
