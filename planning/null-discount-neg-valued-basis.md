# Null discount rate + negatively-valued basis variables: why inconsistency persists

Question that motivated this note: **under the null (0%) discount-rate case, why
do we still observe non-null dynamic inconsistency when there are
negatively-valued harvesting decisions (CM-CE) in the model basis?**

Short answer: the inconsistency at 0% is not a discounting phenomenon, and the
negatively-valued CM-CE allocations are not a bug in the basis — they are the
mechanism. Details below, mapped to where the paper already says each piece.

## 1. The 0% rate removes the timing motive, not the structural one

Dynamic inconsistency in this model comes from the interaction of:

- (a) the bounded-deviation harvest-flow constraint linking consecutive periods
  (`H_{t+1} - (1-alpha) H_t >= 0`, `H_{t+1} - (1+beta) H_t <= 0`; thesis
  eqs. 3-4/3-5, paper eq. `eq:openloop`), and
- (b) the state transition — the future planner inherits the realized (depleted)
  forest and re-solves with a **fresh** flow constraint anchored to her own
  period-1, not carried from the announced trajectory (Methods, "sequential-
  replanning simulator", modeling decision 1).

The discount factor is uniform across periods, so it cancels out of the
consistency conditions (thesis ch. 3, pp. 58-59; paper Discussion,
"discount-rate nuance"). At delta = 1 the objective is indifferent to timing,
but the flow constraint still binds and the state still changes. Hence the grid
result: flow-constrained occurrence is **100% at 0%** (vs 47-86% at 2-6%).

## 2. Why negative-value variables are in the basis at all

In the open-loop solve, a negatively-valued CM-CE allocation (harvest cost >
timber value, driven by the high per-ecoclass access/road cost; see
`instance/feis.py`) is basic **only because the flow row is binding**:

- Its direct objective contribution is negative.
- But it relaxes a binding flow constraint — under NDY (`alpha = 0`),
  `H_{t+1} >= H_t` must hold even in periods where the positive-value strata
  cannot supply the promised volume, so CM-CE area enters as
  **constraint-filler** whose shadow value via the flow row exceeds its cash
  loss.
- In LP terms the variable is priced against the constraint, not in isolation:
  it is in the optimal basis *despite* losing money.

These are the thesis's "inconsistent variables" (paper Results, "Role of
disequilibrium structure"): area allocations whose only function is to relax
the binding flow constraint in the plan.

## 3. Why the replanner abandons them

At replan tau the state is realized (the positive-value over-mature pulse is
depleted) and the new subproblem re-anchors its own flow constraint. The CM-CE
allocation no longer buys relaxation of a bind the new planner does not face —
it is now just a money-losing harvest — so she drops it.

The announced tail is then **strictly suboptimal or outright infeasible** from
the realized state, which is exactly what the objective-gap diagnostic confirms
(on landbase 1 / NDY: 13-14 of 15 replan periods at every discount rate,
including 0%). So the 0% divergence under flow-constrained policies is genuine
inconsistency, not alternate-optimum churn.

## 4. Why the divergence is *larger* at 0%

At a positive rate, discounting penalizes the loss-making harvest a second time
and discriminates among timings of the positive-value harvests, disciplining
the plan. At 0% there is:

- no cost to parking the negative-value filler in whichever period best smooths
  the announced flow, and
- no benefit to the successor planner in honouring any particular promise.

So the open-loop plan leans hardest on CM-CE filler at 0% and the realized
trajectory abandons it wholesale — consistent with the grid result that mean
relative divergence and total-volume shortfall are markedly larger at 0% than
at 2-6% (landbase 1 / NDY).

Corollary for the metric: at 0% the flat objective also admits near-tie optima,
so the trajectory-divergence metric flags the **NHF control** too — but the
objective-gap diagnostic shows the no-flow tail is largely still optimal there
(alternate optima, not genuine inconsistency). Flow-constrained 0% divergence,
by contrast, is genuine per the diagnostic. This distinction is already in the
Discussion ("discount-rate nuance") and must be kept whenever 0% numbers are
quoted.

## 5. The tell vs the fuel

Keep straight in the write-up:

- **Fuel**: disequilibrium forest structure (pulse of immediately harvestable,
  financially over-mature volume in front of a regulated future that cannot
  sustain it) + the flow-constraint link. Landbase 2 (CM-CE excluded) still
  shows inconsistency, so negative-value strata are not strictly necessary.
- **Tell**: the negatively-valued CM-CE basis entries make the inconsistency
  directly observable, as announced loss-making commitments that sequential
  re-optimization abandons.

## Pointers

- Paper: `paper/sections/results.tex` (occurrence 100% at 0%; gap-diagnostic
  counts), `paper/sections/discussion.tex` (discount-rate nuance; drivers).
- Thesis basis: ch. 3, pp. 58-59 (discount factor drops out of consistency
  requirements); eqs. 3-4/3-5 (flow form).
- Code: `src/fresh_daugherty/instance/feis.py` (CM-CE access cost, the
  negative-value driver); `src/fresh_daugherty/lp.py` (LP builder);
  `tests/test_thesis_data.py::test_negatively_valued_strata_are_cm_ce`,
  `tests/test_feis_data.py` (sign checks).
