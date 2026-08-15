# fresh-daugherty Release Notes

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
