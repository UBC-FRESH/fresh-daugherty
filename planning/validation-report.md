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

### Mature-volume derivation: disclosure + independent cross-check (P1.4)

The five mature (existing over-mature) vegetation types' standing volumes are
**back-computed from the Table 5.4 PNV anchors**
(`model.mature_volume_mcf = pnv_period1 / net_price`). Consequently, matching
Table 5.4 is **by construction, not independent validation** — this is now
disclosed here and in the paper.

The genuine independent check is `feis.mature_volume_crosscheck()`, which
compares the back-computed volumes against the FEIS standing-volume-by-age
curves evaluated at each mature type's age (a source independent of Table 5.4):

| Mature type | age | back-calc (MCF/ac) | FEIS indep (MCF/ac) | FEIS/back-calc |
|---|---|---|---|---|
| CH-CW sawtimber | 195 | 10.3 | 13.1 | 1.28 |
| CH-CW two-storied | 115 | 4.7 | 11.8 | 2.53 |
| CD-CP sawtimber | 125 | 3.8 | 9.2 | 2.45 |
| CR-CF sawtimber | 225 | 8.4 | 10.7 | 1.27 |
| CM-CE sawtimber | 175 | n/a (neg. PNV) | 6.4 | n/a |

The two sources agree in **order of magnitude**; the back-calc is
systematically lower (1.3-2.5x), consistent with the thesis's Table 5.4 PNV
reflecting the merchantable sawtimber/premium-log portion net of costs rather
than total standing volume. This is reported honestly as a fidelity caveat; the
mature types use the thesis-faithful back-calc (so the thesis's own Table 5.4
anchors are reproduced), with the FEIS curves as the independent order-of-
magnitude cross-check.

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

Headline findings below are the BUG-ERA record (superseded). For the corrected,
current results see `results/experiments/grid.csv` + `REPRODUCIBILITY.md` and
the note at the end of this section.

- ~~Dynamic inconsistency occurs in 100% of cells~~ (bug-era).
- ~~Discount rate has no effect~~ (bug-era; this was an artifact of an inert
  objective — a theme-lowercasing bug zeroed the NPV coefficients).

> **Superseded (post-#46, current).** With the corrected stack (inert-objective
> fix, replan state-carryover fix, mature-volume Table 5.4 fidelity fix, corner
> -artifact fix, full 18-landbase grid): flow-constrained occurrence 73% vs NHF
> 38% (NHF consistent at 4-6%); NDY is the most inconsistent policy (86%);
> inconsistency occurs at every discount rate with magnitude rate-dependent
> (larger at 0%); landbase occurrence 50-100%. The objective-gap diagnostic
> separates genuine inconsistency from alternate LP optima. See
> `results/experiments/grid.csv` and `planning/thesis-formulation.md`.

Young-growth (regulated) forests under the open-loop even-flow plan show the
"declining non-declining yield" phenomenon (the plan over-commits the forest;
the realized replanned trajectory cannot sustain the promised cut). The
consistent-solution (subgame-perfect) construct is documented in the master
plan; computing it exactly is a follow-on (the thesis's "generating consistent
solutions"). The regeneration-mandate precommitment remedy is noted (the
reproduction's harvest regenerates to age 0 by construction).

## Data sourcing (post-v0.1.0a1): Umpqua FEIS secured

Following the paper-review finding that the data-availability claim was
overstated, the archival documents were located. The 1990 Umpqua FEIS (Final
Environmental Impact Statement, LRMP) is secured (HathiTrust record
002439528, full-view public domain, held locally in `tmp/`, gitignored).

Real Umpqua economics extracted (FEIS main volume; corroborate the thesis
anchors with primary data, not just the thesis's secondary summary):

- Economics framework (FEIS ch. II): PNV, 4% discount rate, constant real
  1982 dollars, purchaser logging/road/slash costs rising at a 1% real rate
  for the first 50 years — exactly the thesis's structure.
- Stage II "Financial Analysis of Timber Prescriptions" (FEIS ch. II, p.
  II-6): mature-timber PNV $1,800-$7,700 per acre (roads not required), 6-22%
  less with road construction; immature managed/unmanaged prescriptions
  $27-$290 per acre (precommercial thins, fertilization, 2-3 commercial thins
  before harvest); CH/CW ecoform consistently highest and strongly positive;
  mountain hemlock (CM-CE) timber prescriptions lose money (best case loses
  $4-$17/ac; natural-regen + harvest-without-intermediate-treatments loses
  $92/ac on 10-yr managed, $312/ac on low-cost non-accessed mature, $894/ac
  on moderate-cost accessed mature lands). This is the negatively-valued
  stratum, confirmed from primary data.
- Benchmark table (Table II-1A): ASQ / LTSY / PNV / discounted costs /
  benefits / old-growth per benchmark alternative.

Still in a separate bound volume (not in this 711-page FEIS main volume):
FEIS Appendix B (the FORPLAN model + detailed per-age yield schedules and the
full per-prescription financial-analysis tables). That volume is the final
item to source for pointwise-exact yield curves; the yield-curve *shapes* are
already grounded in the LRMP CMAI culmination ages and the economics are now
grounded in the FEIS Stage II analysis.

The 1987 DEIS (Daugherty's exact data vintage) is located on HathiTrust
(record 002547999) but is bot-blocked to scripted download; it would give the
exact 1987 data.

## Real-data reconstruction (post-v0.1.0a1 fidelity upgrade, issue #13)

The Umpqua FEIS Appendix B (the FORPLAN analysis volume) is secured
(HathiTrust record 002439528, OCR text, public domain, held in `tmp/`,
gitignored). This replaces the calibrated reconstruction with the real Umpqua
FORPLAN data:

- `tmp/extract_umpqua_feis.py` parses the Appendix B OCR text into the typed,
  provenance-stamped, committed data module `instance/umpqua_feis.py`: 17
  per-age yield tables (volume removed MCF/ac by age, per ecoclass x
  prescription x intensity x emphasis, with CMAI markers), site indices
  (Table B-39), stumpage/logging/manufacturing economics by species (Table
  B-65), and Douglas-fir price-diameter/pond values (Table B-66).
- `instance/feis.py`: accessors (`real_yield_table`, `real_yield_curve`,
  `real_ecoclass_net_revenue`). The real yield curves' rotation ages match the
  thesis's Table 5.2 ranges; the per-ecoclass net revenues (FEIS stumpage x
  BF/CF, less access cost) are CH-CW \$745, CD-CP \$912, CR-CF \$779, CM-CE
  -\$391/MCF (the negatively-valued stratum, from real data + access cost).
- `model.py` builds the case-study on the real yield curves; `lp.py` uses the
  real economics. The open-loop LP solves on real data (landbase 1 and the
  young-growth landbase 9 both optimal, non-degenerate).
- **The dynamic-inconsistency result reproduces on real Umpqua FORPLAN data**:
  landbase 1 (all mature) open-loop even-flow plan projects ~85-89k MCF/period;
  the realized sequential-replanned trajectory is volatile and delivers ~54%
  less total volume (mean |relative deviation| 55%).

The paper's data section is updated to describe the real-data reconstruction
(the 1987 DEIS, Daugherty's exact vintage, is the one document not yet
obtained in machine-readable form; the 1990 FEIS lineage is used).

Real-data experiment grid (48 cells, horizon 15, rolling horizon):
occurrence 100%; discount-rate invariant (mean deviation 0.563 at 0-6%); by
landbase 1/2/9/10 mean deviations 0.41/0.41/0.63/0.81; total realized volume
below projected by 40%/38%/57%/80% respectively. The dynamic-inconsistency
finding reproduces on the real Umpqua FORPLAN data.

## 1987 DEIS secured (Daugherty's exact data vintage)

The 1987 Umpqua Draft EIS (the document Daugherty 1991 used) is secured
(HathiTrust record 002547999; the `mdp-39015025002364` item, OCR text, public
domain, held in `tmp/`, gitignored). Its managed yield tables match the 1990
FEIS Appendix B volumes exactly, AND they carry the per-age PNV columns that
the 1990 OCR garbled — Daugherty's exact data, with both volumes and per-age
PNV. The reproduction's dataset of record is the Umpqua FORPLAN data (1990
FEIS lineage, confirmed against the 1987 DEIS); the 1987 DEIS enables a
pointwise-exact-vintage extraction (including the per-age PNV) as a final
refinement.

### Exact-vintage validation (issue #15)

The 1987 DEIS managed yield tables (Daugherty's exact vintage) are parsed.
The model's per-cell max Faustmann LEV (`instance.feis.model_lev`, from the
real FEIS yield curve + real per-ecoclass net revenue) reproduces the thesis
Table 5.3 anchors' *signs and ordering*: productive ecoclasses positive, the
CM-CE prescriptions non-positive (the negatively-valued stratum), and optimal
rotations within the thesis Table 5.2 ranges. Exact LEV magnitudes differ
(the thesis's LEV accounting — treatment costs and the exact volume
convention — is not fully recoverable from the OCR); the structural features
driving the inconsistency are reproduced exactly. Test:
`tests/test_feis_data.py::test_model_lev_reproduces_anchor_signs`.

## Reproducibility base (license-clean)

The Umpqua documents are US government (USDA Forest Service) works — public
domain (17 U.S.C. section 105) — but the HathiTrust/Google digitized scans and
OCR carry Google's request that the images and OCR not be re-hosted,
redistributed, or used commercially. Accordingly the raw scans/OCR stay in the
gitignored `tmp/` and are NEVER committed. The license-clean reproducibility
base is:

- `src/fresh_daugherty/instance/umpqua_feis.py` (tracked): the derived,
  structured, factual dataset (numbers are not copyrightable), with the source
  citations in its module docstring.
- `scripts/extract_umpqua_feis.py` (tracked): the one-time extraction script
  that regenerates the dataset from the source scan.
- Source citations (public domain, HathiTrust): FEIS Appendix B record
  002439528; 1987 DEIS record 002547999; FEIS main volume record 002439528.
