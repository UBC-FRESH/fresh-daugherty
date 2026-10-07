# fresh-daugherty Release Notes

## 0.2.0 — 2026-10-07

The archived benchmark record behind the CJFR manuscript "Dynamic
inconsistency in open-loop LP forest plans: an open, reproducible benchmark of
Daugherty (1991)". Phases P9-P19 (see `CHANGE_LOG.md` and `ROADMAP.md`).

- **Extensions** E1-E4 (P9-P12): declining discount rates, a calibrated
  max-harvest cap, a revenue-denominated flow, a rolling-mean flow; curated
  supplement (`supplementary/`, P13).
- **Review analyses** (P15): four replanning institutions (rolling or fixed
  horizon, reset or carried flow history), objective-gap diagnostic on every
  grid, tolerance and window sensitivity, seed sensitivity, thesis comparisons
  on matched populations.
- **Fidelity fixes** (P14, P16-P18): E3 announced plan; gap-diagnostic bound
  composition; minimal, recorded loosening of history bounds; landbases
  rebuilt from the thesis's descriptions; mature-volume calibration to Table
  5.4; the thesis's terminal constraints (p. 77) on every flow-constrained
  run; young-age yields on the calibrated Chapman-Richards shape.
- **Final audit** (P19): terminal-rotation sensitivity
  (`grid_terminal_rotation_model.csv`); every manuscript number tracked by an
  analysis script.
- **Records**: all grids regenerated at `35f6a65` (sensitivity at `545d8ca`);
  every record carries `fd_commit`. Records produced before the version bump
  carry `fd_version=0.1.0b1`; `fd_commit` identifies the source.
- Headline (periods 2-11): 178/360 flow-constrained scenarios inconsistent
  (49%); exact tail problem 1/360.

## 0.1.0a2 — 2026-08-15

Real-data reconstruction. The case study is now built from the **real Umpqua
FORPLAN data** (the 1990 FEIS Appendix B yield tables + economics, extracted
from the public-domain HathiTrust scan into the typed, provenance-stamped
module `instance/umpqua_feis.py`), replacing the v0.1.0a1 calibrated
reconstruction.

- Real per-age yield curves per ecoclass x prescription x intensity (FEIS
  Appendix B); real per-ecoclass net revenues (CM-CE negatively valued,
  -$391/MCF, from real stumpage + access cost).
- The dynamic-inconsistency result reproduces on the real data (landbase 1:
  realized ~54% below the open-loop even-flow projection; 100% occurrence
  across the experiment grid; discount-rate invariant).
- Exact-vintage validation against the 1987 DEIS (Daugherty's exact data).
- License-clean reproducibility base: the derived typed dataset + the tracked
  extraction script (`scripts/extract_umpqua_feis.py`) + source citations;
  raw scans stay gitignored (HathiTrust/Google no-redistribute terms).
- Paper updated to the real data; references completed (Martin/Gunn/Richards
  2017, Paradis et al. 2013, McQuillan 1986 added).

## 0.1.0a1 — 2026-08-14

First public alpha. An open, reproducible reproduction of Daugherty (1991),
*Credibility of Long Term Forest Planning: Dynamic Inconsistency in Linear
Programming Based Forest Planning Models*, built on ws3.

- **Case-study instance** (Phase 1): the Umpqua National Forest FORPLAN
  case-study reconstructed in ws3 — transcribed thesis structure + anchor
  tables (Tables 5.1-5.5), a documented reconstruction calibrated to the
  Table 5.3/5.4 anchors (yield shapes grounded in the Umpqua LRMP CMAI
  culmination ages), and the 18-landbase initial conditions.
- **Open-loop LP** (Phase 1): the NPV-max harvest-scheduling LP (Model I; 4%
  discount, +1%/yr price escalation, even-flow or target-flow harvest policy).
- **Sequential-replanning simulator** (Phase 3): reproduces the thesis's
  iterative LP simulation of sequential replanning; rolling or shrinking
  horizon; inconsistency metrics.
- **Experiments** (Phase 4): occurrence/magnitude grid over landbases x
  discount rates x harvest-flow policies.
- **Reproduced findings**: dynamic inconsistency occurs in 100% of simulated
  conditions; occurrence/magnitude is invariant to the discount rate (the
  thesis's counter-intuitive result); tighter harvest-flow constraints
  increase inconsistency; disequilibrium forest structure with negatively
  valued strata drives it.

Known limitations are recorded in `docs/model_semantics.rst` and
`planning/validation-report.md` (reconstruction fidelity; Model I vs the
thesis's Model II; simulator horizon convention; regenerated-prescription
choice; landbases 3-8).

## 0.1.0a0 — 2026-08-14

Initial repository scaffold and master plan.
