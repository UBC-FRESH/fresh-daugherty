Model Semantics
===============

The model is the Daugherty (1991) case-study reproduced in ws3. This page
records exactly what it computes and its known limitations.

The open-loop LP
----------------

A strata-based long-term timber harvest-scheduling LP. The forest is
partitioned into development types (strata) by ecoclass, prescription, and
age; the decision allocates stratum area to harvest over a 150-year horizon
(15 x 10-year periods). The objective is maximization of present net value
(PNV) at a 4% discount rate, with delivered-log prices escalating at 1%/yr
for the first 50 years. A harvest-flow (even-flow) constraint ties each
period's harvest volume to within a tolerance of the reference period. Harvest
regenerates the stand to age 0 (mature stands convert to the base managed
prescription; managed stands regenerate to themselves).

This is a Model I formulation. Daugherty (1991) used Model II; the
dynamic-inconsistency result is a property of the objective x flow-constraint
x forest-structure interaction, not the variable-aggregation scheme (Gunn
2007, ch. 16 covers the Model I/II/III distinction). The ws3 Model II path is
stubbed and is a deferred ws3 enhancement.

The case-study data
-------------------

The thesis gives the case-study structure and anchor tables (Tables 5.1-5.5)
but not the raw per-age yield curves, per-stratum areas, or detailed
price/cost tables (those are in the archival USDA 1987 Umpqua EIS). The
economics are reconstructed in ``fresh_daugherty.instance.reconstruct`` and
calibrated to the Table 5.3/5.4 anchors; the yield-curve shapes are grounded
in the Umpqua LRMP's documented CMAI culmination ages (Table IV-3). This is a
documented reconstruction with explicit assumptions
(``RECONSTRUCTION_ASSUMPTIONS``), not a transcription.

Dynamic inconsistency
---------------------

The open-loop LP is solved once over the full horizon (open-loop: the planner
precommits future planners). The sequential-replanning simulator
(``fresh_daugherty.replan``) re-solves from the realized state each period.
The open-loop plan's projected harvest diverges from the realized replanned
trajectory: the plan is not followed, so it is not a credible basis for
policy. This is the failure of Bellman's principle of optimality, reproduced.

Known limitations
-----------------

- **Reconstruction fidelity**: the case-study economics are a documented
  reconstruction calibrated to the thesis anchors (PNV magnitudes match to
  ~1%; rotation ages are approximate, because the thesis's irregular rotation
  pattern encodes the unavailable Umpqua yield tables).
- **Model form**: Model I (not the thesis's Model II, which ``ws3`` does not
  yet compile with harvest-flow constraints); the two are equivalent only when
  they encompass the same management alternatives.
- **Replanning institution**: by default each replan covers a full horizon
  rolled forward from the realized state with a fresh flow constraint (rolling
  horizon, reset flow history), as in the thesis. ``rolling_horizon=False``
  keeps the original terminal date and ``carry_flow_history=True`` anchors each
  replan's first harvest to the realized previous harvest; with both, each
  replan solves the exact tail of the original problem (the null test in
  ``tests/test_replan.py``). History-derived bounds (carried anchor,
  realized-history rolling-mean floor) that are infeasible from the realized
  state are loosened minimally and the loosening is recorded
  (``replan.minimal_history_relaxation``).
- **Regeneration**: a harvested stand regenerates under a fixed prescription
  (mature stands under planting, managed stands under their own prescription),
  and the objective has no treatment costs or commercial thinnings, so the
  thesis's choice of management intensity at regeneration is not represented
  (probe and decision: ``planning/p16-regen-choice-probe.md``).
- **Landbases**: all eighteen are constructed from the thesis's descriptions
  (pp. 78-80, Table 5.5); every choice the thesis leaves open is listed in
  ``instance.landbases.LANDBASE_ASSUMPTIONS``.
- **Terminal constraints**: as in the thesis (p. 77), every flow-constrained
  run requires the final-period standing volume to be at least 80% of the
  average inventory of the forest regulated under the regeneration
  prescriptions, and caps the final-period harvest at 120% of its long-term
  sustained yield, both at the highest-PNV rotations
  (``lp.regulated_forest_targets``); not used without a flow policy or with the
  E2 cap (thesis p. 80). Every record also carries the metrics on the thesis's
  observation window, periods 2-11 (``*_2_11`` columns).
- **Young-age yields**: below the first tabled FEIS age, yield curves follow
  the cell's calibrated Chapman-Richards shape scaled to the first FEIS value.
- **Mature-stand calibration**: mature volumes are flat over age and chosen so
  that the model's own discounted value of a period-1 harvest (4%) equals the
  thesis's Table 5.4; period-2 values are within 13% except CM-CE
  (``model.mature_value_check``).
