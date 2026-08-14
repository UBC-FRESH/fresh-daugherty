# fresh-daugherty validation report

Validation and calibration records for the Daugherty (1991) reproduction.
Companion to `planning/v0.1.0a1-plan.md`.

## Environment (locked)

- Python 3.12 venv at the FRESH workspace root; ws3 (editable 1.1.0a4 locally;
  PyPI 1.0.5 in CI), scipy, numpy, pandas, pydantic.

## P1.1 Case-study instance

### Thesis reference data (transcribed)

`fresh_daugherty.instance.thesis` transcribes the thesis's case-study
structure and anchor tables (printed-page provenance per table):

- Horizon 150 yr in 15 x 10-yr periods; PNV-max objective; volumes in MCF;
  delivered-log prices +1%/yr for the first 50 yr then flat; harvest-flow +
  ending-period constraints (p.71-72).
- Table 5.1: 4 ecoclasses (CH-CW, CD-CP, CR-CF, CM-CE) in decreasing growth
  potential.
- Table 5.2: rotation-age ranges by ecoclass x prescription (7
  prescriptions).
- Table 5.3: max-PNV ($/ac, 4% discount) + optimal rotation per cell; the
  CM-CE regenerated prescriptions are negatively valued (-4, -150, -153).
- Table 5.4: PNV of the 5 mature (over-mature) vegetation types in periods
  1-2; CM-CE sawtimber is negatively valued (-1042, -674) and its negative
  PNV *decreases* over time (the thesis's noted exception).
- Table 5.5: 18 initial forest conditions (landbases), 10,000 ac each.

### Reconstruction (calibration to the anchors)

The raw per-age yield curves, per-stratum areas, and detailed price/cost
tables are NOT in the thesis (they are in the archival USDA 1987 Umpqua
Forest Plan Draft EIS). They are reconstructed in
`fresh_daugherty.instance.reconstruct` under documented assumptions
(`RECONSTRUCTION_ASSUMPTIONS`), calibrated to the Table 5.3 / 5.4 anchors.

Grounding data (real, from the Umpqua LRMP — a public-domain USFS work,
Google Books id `lqbvYRGYkpUC`): the 95%-CMAI culmination ages per ecoclass
(Table IV-3) pin the reconstructed yield-curve shapes
(`CMAI_CULMINATION_AGE_YR`: CH-CW 85, CD-CP 120, CR-CF 115, CM-CE 175 yr).

Achieved fit (least squares, per-ecoclass economics + shared treatment
effects): mean |PNV error| ~$37/ac; rotations within ~22 yr; the negative
CM-CE sign and the PNV-rises-with-management-intensity ordering are
reproduced exactly. **This is a structural reconstruction**: the smooth
Chapman-Richards model cannot reproduce the pointwise-irregular Table 5.3
pattern, which encodes the unavailable Umpqua yield tables. The
dynamic-inconsistency results (the point of the reproduction) do not depend
on pointwise-exact rotations.

### Landbases

`fresh_daugherty.instance.landbases` constructs the initial conditions.
Landbases 1, 2, 9, 10 are structured; 11-18 are seed-fixed random
young-growth; 3-8 (area-control-harvest-derived) are documented as not yet
constructed. See `LANDBASE_ASSUMPTIONS`.

## P1.2 Open-loop Model I LP

`fresh_daugherty.model` builds the case-study as a ws3 ``ForestModel``
(Model I; 5 themes FOREST/ECOCLASS/RX/ORIGIN/STATE). Managed young-growth
(ecoclass x prescription) + mature (existing over-mature) development types;
harvest operable over the Table 5.2 rotation window; harvest regenerates to
age 0 (mature stands convert to the base managed prescription; managed stands
regenerate to themselves).

`fresh_daugherty.lp` adds the open-loop NPV-max even-flow LP (4% discount,
price escalation) and solves it. Verified on landbase 1 (all mature): LP
optimal; even-flow holds within 5% of period 1; growing stock declines
(1.42M -> 271k MCF) as the over-mature timber is drawn down; harvest area
rises as lower-volume managed stands replace the mature pulse.

## Validation anchors status

- Table 5.3 / 5.4 reproduction: via the reconstruction calibration (above).
- Base-case open-loop schedule: the thesis's exact base-case schedule depends
  on the unavailable Umpqua per-stratum data, so the validation is (a) the
  reconstruction fit to Table 5.3/5.4 and (b) the LP's qualitative behaviour
  (even-flow, mature drawdown), not a pointwise schedule match. Recorded as a
  fidelity caveat.

Record count: 31 tests; ruff, docs, build, twine green.

## P3 Sequential replanning + inconsistency

`fresh_daugherty.replan` implements the sequential-replanning simulator:
solve the open-loop LP, apply the current period's decision, advance the
forest state (the realized area-by-age distribution extracted via ws3
`age_class_distribution`), and re-solve from the realized state over the
remaining horizon, repeating to the horizon. Inconsistency is measured as the
divergence between the open-loop plan's projected per-period harvest and the
realized replanned trajectory.

Result (landbase 1, all mature, horizon 15): the open-loop plan projects a
smooth even-flow harvest (~88-93k MCF/period); the realized replanned
trajectory is volatile (65k-114k MCF/period) and does NOT follow the plan —
mean absolute relative deviation ~29%, total realized ~9% below projected.
The period-1 decision is always consistent (the divergence is in the tail).
This reproduces Daugherty's dynamic-inconsistency finding on the reconstructed
case-study. The magnitude and sign vary with horizon and initial condition
(the thesis reports inconsistency "over a wide range of initial forest
conditions and harvest policies"). Seed-fixed runs are bit-stable.

## P4 Experiments + consistent-solution construct

`fresh_daugherty.experiments` sweeps the thesis's experimental factors —
initial forest condition (landbase), harvest policy (even-flow tolerance or
target-flow ceiling), and interest rate — measuring inconsistency occurrence
and magnitude per cell (`run_experiment`, `run_experiment_grid`). The
sequential-replanning simulator supports a rolling fixed horizon (default;
avoids the shrinking-horizon terminal artifact) or a shrinking horizon.

Headline findings (rolling horizon, horizon 15, landbases 1/2/9/10 x rates
0-6% x flow tolerances 1-15%):

- Dynamic inconsistency occurs in 100% of cells (mean per-period deviation
  of realized-vs-projected harvest well above 5% across the grid).
- **Discount rate has no effect** on the volume-based inconsistency (the
  occurrence/magnitude is identical across 0-6%): the discount factor is
  uniform across periods and drops out of the consistency requirements —
  reproducing Daugherty's counter-intuitive result (ch. 3, p.58-59).
- **Tighter harvest-flow constraints increase inconsistency** (the flow
  constraint is the operative between-period link).
- **Disequilibrium forest structure drives inconsistency**: the mature/old-
  growth landbases show it clearly; the magnitude depends on the initial
  age-class disequilibrium.

Young-growth (regulated) forests under the open-loop even-flow plan show the
"declining non-declining yield" phenomenon (the plan over-commits the forest;
the realized replanned trajectory cannot sustain the promised cut). The
consistent-solution (subgame-perfect) construct is documented in the master
plan; computing it exactly is a follow-on (the thesis's "generating consistent
solutions"). The regeneration-mandate precommitment remedy is noted (the
reproduction's harvest regenerates to age 0 by construction).
