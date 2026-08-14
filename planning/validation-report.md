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
