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
- **Model form**: Model I (not the thesis's Model II); noted as a fidelity
  caveat, not a deviation of substance.
- **Simulator horizon**: the default rolling fixed horizon avoids the
  terminal-period artifact of a shrinking horizon; both are available.
- **Regenerated-prescription choice**: harvest regenerates to the base managed
  prescription; the full prescription-choice fan-out is a refinement.
- **Landbases 3-8** (area-control-harvest-derived) are documented as not yet
  constructed.
