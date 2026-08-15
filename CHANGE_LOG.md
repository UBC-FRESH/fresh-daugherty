# fresh-daugherty Change Log

Append-only project narrative, reverse-chronological.

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
