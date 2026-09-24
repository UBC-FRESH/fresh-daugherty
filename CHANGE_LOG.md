# fresh-daugherty Change Log

Append-only project narrative, reverse-chronological.

## v0.2.0 (unreleased) — P9–P13 complete (scope expansion done)

Phase 13 (E5: curated supplementary material + manuscript pointers) on
`feature/p13-supplement` (PR #74 merged) + `fresh_daugherty_manuscript@main`.

- P13.1+P13.2 (#67, #68): `supplementary/` tree (README index + 9 pages + PNG
  figures) and `scripts/build_supplement.py` — one tracked command regenerates
  the whole supplement from the tracked records (re-runs the four extension
  analysis scripts by default; link targets existence-checked; idempotent).
  Figure PDFs are now bit-stable (null CreationDate metadata).
- P13.3 (#69): manuscript pointers rewritten to specific supplement
  sections/tables/records (Data Availability, Results intro + Fig. 1 + Table
  1, Methods data paragraph, Software availability) in
  `fresh_daugherty_manuscript` on `main` (Overleaf-synced).

## v0.2.0 (unreleased) — P9–P11 complete; P12 in progress

Phase 12 (E4: rolling-mean NDY) on `feature/p12-rolling-mean-ndy`.

- P12.1 (#64): `lp.py` — `flow_geometry="rolling_mean"` + `flow_window`;
  backwards-facing rolling-mean NDY rows added post-compile via ws3's cflw
  coefficient worker; k=1 degenerates exactly to pointwise NDY (regression);
  composes with the E3 revenue denominator.
- P12.2 (#65): `replan.py` — anchoring readings (`rolling_realized_history`:
  within-plan vs realized-history windows) + opt-in solver-note recording for
  infeasible-floor fallbacks.
- P12.3 (#66): E4 grid run and tracked: 288 cells (18 landbases x 4 rates x
  windows {2,3} x 2 anchoring readings) via `fresh-daugherty
  grid-rolling-mean`; records
  `results/experiments/grid_rolling_mean{,_trajectories,_gaps}.csv`;
  analysis `scripts/analyze_p12_rolling_mean.py` ->
  `results/analysis/p12_rolling_mean/` + writeup. Headlines: constraint
  SHAPE is not the margin (within-plan rolling mean ≈ pointwise NDY: 89% vs
  86% occurrence); the ANCHORING institution is — realized-history anchoring
  mitigates (occurrence 65-72%, magnitude 0.07) but the floor often cannot
  be sustained (relax_share 19-32% of periods at positive rates).

## v0.2.0 (unreleased) — P9, P10 complete; P11 in progress

Phase 11 (E3: value-denominated flow constraints) on `feature/p11-value-flow`.

- P11.1 (#61): `lp.py` — `flow_denominator='volume'|'revenue'`; the
  bounded-deviation flow rows carry undiscounted net revenue (volume x
  escalated net price) under the revenue form. Volume form bit-identical
  (regression); revenue NDY verified non-declining in revenue.
- P11.2 (#62): `replan.py` — `_period_net_revenue` + `collect_revenue` on the
  gap diagnostic; dual (volume + revenue) trajectory records; revenue
  divergence scorable with the standard metric.
- P11.3 (#63): E3 grid run and tracked: 864 cells (18 landbases x 4 rates x
  6 policies x 2 denominators) via `fresh-daugherty grid-value-flow`;
  records `results/experiments/grid_value_flow{,_trajectories,_gaps}.csv`;
  analysis `scripts/analyze_p11_value_flow.py` -> `results/analysis/p11_value_flow/`
  + writeup. Headlines: (1) revenue denominating makes inconsistency MORE
  pervasive (flow-constrained occurrence 98-100% vs 58-86% volume; magnitude
  ~2x) — the denomination unit is not the operative margin; (2) the CM-CE
  filler channel confirmed as the tell, not the fuel — revenue NDY drives
  CM-CE basis entries to exactly zero (volume NDY: 2.5-3.5% of projected
  volume on landbase 1), yet inconsistency persists.

## v0.2.0 (unreleased) — P9 complete; P10 in progress

Phase 10 (E2: max-harvest-cap even-flow search) on `feature/p10-cap-search`.

- P10.1 (#57): the cap form is the existing `target_flow_mcf` per-period
  ceiling (zero lower bound; always feasible); documented as the E2 form;
  tests (loose-cap bit-identity with NHF; tight-cap compliance).
- P10.2 (#58) + P10.3 (#59): `evenflow.py` — typed `EvenFlowCriteria`
  (defaults: |slope| <= 1% of mean/period; fluctuation <= 5%; CV <= 5%),
  `assess_even_flow`, and `calibrate_even_flow_cap` (bisection to the loosest
  cap whose REALIZED replanned trajectory is even; full iteration history).
- P10.4 (#60): E2 grid run and tracked: 72 cells (18 landbases x 4 rates) via
  `fresh-daugherty grid-cap-search`; records
  `results/experiments/grid_cap_search{,_trajectories,_gaps}.csv`; analysis
  `scripts/analyze_p10_cap_search.py` -> `results/analysis/p10_cap_search/`
  + writeup. Headline: cap calibration ELIMINATES dynamic inconsistency —
  0% occurrence at every rate (mean divergence 0.04-0.96%), 96.4% of tail
  periods optimal under the gap diagnostic, vs 78-100% occurrence for the
  NDY control; the calibrated even-flow level (~9,400 MCF/period on
  landbase 1) sits ~8% below the NDY plan's announced level.

Phase 9 (E1: time-varying discount-rate shapes) on `feature/p9-discount-shapes`.

- P9.1 (#53): `instance/discount.py` — typed, provenance-stamped
  discount-rate path records (`constant` / `linear` / `inverse-j` families);
  the fixed E1 parameter set (`linear-4pc-0pc`, `linear-6pc-0pc`,
  `invj-4pc-k1`, `invj-4pc-k2`); per-period factor vectors with the constant
  family bit-identical to the core scalar convention; validation and tests
  (`tests/test_discount.py`).
- P9.2 (#54): `lp.py` — the open-loop LP consumes a per-period
  discount-factor vector; the scalar `discount_rate` entry point is a wrapper
  over a `constant` path (bit-identical objective and optimal plan, verified
  by regression test); `discount_path` kwarg wires any E1 path into the
  objective (`tests/test_lp.py`).
- P9.3 (#55): E1 experiment grid run and tracked. `replan.py`/`experiments.py`
  plumb `discount_path` through the simulator and gap diagnostic; new
  `run_discount_path_grid` + `fresh-daugherty grid-discount-paths` entry point;
  tracked records `results/experiments/grid_discount_paths{,_trajectories,_gaps}.csv`
  (432 cells: 4 paths x 18 landbases x 6 policies, each with the objective-gap
  diagnostic; provenance columns fd/ws3 versions). Headline: declining-rate
  paths do NOT mitigate — occurrence 98-100% across all four paths (vs 47-71%
  at constant 2-6%), with mean divergence 0.17-0.24 (inverse-j highest).
- P9.4 (#56): E1 analysis + write-up. `scripts/analyze_p9_discount_shapes.py`
  regenerates tables T1-T4 + figures F1-F2 from the tracked records into
  `results/analysis/p9_discount_shapes/`, plus `writeup.md` (draft for the
  manuscript's Extensions section). Findings: declining rates make
  inconsistency MORE pervasive (flow-constrained occurrence 98-100% vs 47-86%
  at constant 2-6%; magnitude 0.16-0.20 vs 0.07-0.11); and the NHF control
  cells separate a second, preference-level (Strotz) channel — under
  declining paths the no-flow cells diverge at 100% occurrence with gap
  diagnostic confirming genuine strict suboptimality/infeasibility (30-61% +
  7-14% of tail periods), unlike the constant-0% tie-churn case.

## v0.2.0 planning — 2026-09-23

Scope expansion agreed with co-author J. Fuchs (BOKU), who joins the paper;
the manuscript migrated to the Overleaf-linked repo
`ubc-fresh/fresh_daugherty_manuscript` (all manuscript work on `main` there).
Four modelling extensions plus a dissemination extension planned in
`planning/v0.2.0-plan.md`, each evaluated on whether it mitigates or
eliminates dynamic inconsistency against the intact core grid: P9/E1
time-varying discount-rate shapes (#48, children #53–#56); P10/E2
max-harvest-cap even-flow search (#49, children #57–#60); P11/E3
value-denominated flow constraints (#50, children #61–#63); P12/E4
rolling-mean NDY (#51, children #64–#66); P13/E5 curated supplementary
material + manuscript pointers (#52, children #67–#69). Phase branches per
the strict workflow, starting with `feature/p9-discount-shapes`. Companion
analysis note: `planning/null-discount-neg-valued-basis.md`.

## 0.1.0a0 — 2026-08-14

Initial repository scaffold and master plan. No functional pipeline yet.

## 0.1.0a0 — 2026-08-14 (Phase 1)

Phase 1 (case-study instance + open-loop LP, Model I) in progress on
`feature/p1-open-loop`.

- P1.1 Case-study instance: transcribed thesis reference data
  (`instance/thesis.py`); calibrated reconstruction
  (`instance/reconstruct.py`) of the yield/economics model to the Table
  5.3/5.4 anchors, yield-curve shapes grounded in the Umpqua LRMP CMAI
  culmination ages; landbases (`instance/landbases.py`).
- P1.2 Open-loop Model I LP: case-study ws3 model (`model.py`) + NPV-max
  even-flow LP (`lp.py`, 4% discount, price escalation). Verified on
  landbase 1: optimal, even-flow holds, mature timber drawn down.

## 0.1.0a0 — 2026-08-14 (Phase 3)

Phase 3 (sequential-replanning simulator + inconsistency measurement) on
`feature/p3-replanning`.

- `replan.py`: the sequential-replanning simulator (solve, apply period t,
  advance state, re-solve) over the case-study Model I LP, plus
  inconsistency metrics. Reproduces dynamic inconsistency on landbase 1:
  the open-loop even-flow plan is not followed on replan (mean deviation
  ~29%, total realized ~9% below projected); period 1 always consistent;
  seed-fixed bit-stable.

## 0.1.0a0 — 2026-08-14 (Phase 4)

Phase 4 (experiments + consistent-solution construct) on
`feature/p4-experiments`.

- `experiments.py`: experiment runner sweeping landbases x discount rates x
  harvest-flow policies, producing the inconsistency occurrence/magnitude
  table. Rolling-horizon sequential replanning (default) avoids the
  terminal artifact; shrinking-horizon also available.
- Young-growth landbases corrected to regulated forests (full age-class
  distribution); target-flow (AAC ceiling) harvest policy added to the LP.
- Findings: inconsistency occurs across all conditions; discount-rate
  invariant (the thesis's counter-intuitive result reproduced); tighter flow
  -> more inconsistency; disequilibrium structure drives it.

## 0.1.0a1 — 2026-08-14

Phase 5 (validation + docs + release) on `feature/p5-release`; version bumped
to `0.1.0a1`.

- Docs (quickstart, model semantics, CLI reference, architecture) updated to
  the working pipeline; CLI `open-loop`/`replan-run` wired to the real
  implementations.
- RELEASE_NOTES 0.1.0a1 entry; validation record finalized; version bumped.
- Model II (P2) scoped: the reproduction uses Model I (ws3-supported); the
  ws3 Model II LP path is deferred post-v0.1.0a1 (documented rationale).

## 0.1.0a2 — 2026-08-15

Real-data reconstruction release. Case study rebuilt on the real Umpqua
FORPLAN data (FEIS Appendix B); exact-vintage validation vs the 1987 DEIS;
license-clean reproducibility base; paper updated to real data with completed
references.
