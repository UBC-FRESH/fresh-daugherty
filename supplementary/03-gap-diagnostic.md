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
| +/-10% | 0.113 | 0.24 | 0.647 |
| +/-20% | 0.136 | 0.217 | 0.647 |
| -10% | 0.057 | 0.391 | 0.553 |
| -20% | 0.058 | 0.409 | 0.534 |
| NDY | 0.502 | 0.097 | 0.401 |
| NHF | 0.025 | 0.773 | 0.202 |

## By discount rate

| discount_rate | infeasible | optimal | suboptimal |
| --- | --- | --- | --- |
| 0.0 | 0.101 | 0.259 | 0.64 |
| 0.02 | 0.147 | 0.415 | 0.438 |
| 0.04 | 0.169 | 0.374 | 0.456 |
| 0.06 | 0.176 | 0.37 | 0.454 |

Reading: under flow-constrained policies the announced tail is predominantly
**suboptimal** (strictly improvable) or **infeasible** (cannot even be
implemented) from the realized state — genuine inconsistency; under NHF the
tail remains largely optimal except at the lowest rates (flat-objective
tie-churn), which is why the NHF divergence metric is not read as genuine
inconsistency there.
