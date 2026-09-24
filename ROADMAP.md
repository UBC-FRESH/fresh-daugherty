# fresh-daugherty Roadmap

This roadmap is the condensed issue-tracker view of the current project
plan. The detailed plan, design decisions, acceptance criteria, and
validation anchors live in `planning/v0.1.0a1-plan.md`. Keep this roadmap
synchronized with GitHub issues, planning notes, pull requests, and
`CHANGE_LOG.md`.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Skeleton scaffold | [#1](https://github.com/UBC-FRESH/fresh-daugherty/issues/1) | `main` | Complete |
| P1 Case-study instance + open-loop LP (Model I) | [#2](https://github.com/UBC-FRESH/fresh-daugherty/issues/2) | `feature/p1-open-loop` | Complete — PR to `main` pending |
| P2 ws3 Model II LP formulation + solve | TBD | ws3 `feature/model-ii` | Deferred post-v0.1.0a1 (Model I suffices for the core result) |
| P3 Sequential-replanning simulator + inconsistency measurement | [#4](https://github.com/UBC-FRESH/fresh-daugherty/issues/4) | `feature/p3-replanning` | Complete — PR pending |
| P4 Consistent-solution construct + experiments | [#6](https://github.com/UBC-FRESH/fresh-daugherty/issues/6) | `feature/p4-experiments` | Complete (PR [#7](https://github.com/UBC-FRESH/fresh-daugherty/pull/7) merged) |
| P5 Validation vs thesis + docs + release | [#8](https://github.com/UBC-FRESH/fresh-daugherty/issues/8) | `feature/p5-release` | Complete (PR [#9](https://github.com/UBC-FRESH/fresh-daugherty/pull/9) merged; `v0.1.0a1` on PyPI) |
| P6 Paper | [#10](https://github.com/UBC-FRESH/fresh-daugherty/issues/10) | — | Manuscript migrated to the Overleaf-linked repo `ubc-fresh/fresh_daugherty_manuscript` (2026-09); expansion planned as v0.2.0 |
| P7 Good-paper transformation | [#42](https://github.com/UBC-FRESH/fresh-daugherty/issues/42) | — | Open (with open child tasks #43–#45) |
| P8 Rigorous methodology + CJFR pivot | [#46](https://github.com/UBC-FRESH/fresh-daugherty/issues/46) | `feature/p8-rigorous-cjfr` | Complete — merged; `v0.1.0b1` released with Zenodo DOI |
| P9 E1: time-varying discount-rate shapes | [#48](https://github.com/UBC-FRESH/fresh-daugherty/issues/48) | `feature/p9-discount-shapes` | Complete (PR [#70](https://github.com/UBC-FRESH/fresh-daugherty/pull/70) merged) |
| P10 E2: max-harvest-cap even-flow search | [#49](https://github.com/UBC-FRESH/fresh-daugherty/issues/49) | `feature/p10-cap-search` | Complete (PR [#71](https://github.com/UBC-FRESH/fresh-daugherty/pull/71) merged) |
| P11 E3: value-denominated flow constraints | [#50](https://github.com/UBC-FRESH/fresh-daugherty/issues/50) | `feature/p11-value-flow` | Complete (PR [#72](https://github.com/UBC-FRESH/fresh-daugherty/pull/72) merged) |
| P12 E4: rolling-mean NDY | [#51](https://github.com/UBC-FRESH/fresh-daugherty/issues/51) | `feature/p12-rolling-mean-ndy` | Planned — children #64–#66 |
| P13 E5: curated supplementary material + manuscript pointers | [#52](https://github.com/UBC-FRESH/fresh-daugherty/issues/52) | `feature/p13-supplement` | Planned — children #67–#69 |

## v0.2.0 Scope Expansion (2026-09)

Scope expansion agreed with co-author J. Fuchs (BOKU): four modelling
extensions (E1–E4, phases P9–P12) plus a curated-supplement extension (E5,
P13), each evaluated on whether it mitigates or eliminates dynamic
inconsistency against the intact core grid. Detailed plan:
`planning/v0.2.0-plan.md`. The manuscript now lives in the Overleaf-linked
`ubc-fresh/fresh_daugherty_manuscript` repo (all manuscript work on `main`
there); this repo remains the sole source of modelling code, experiment
records, and the supplement.

## Project One-Liner

Reproduce Daugherty (1991) — dynamic inconsistency in LP-based forest
planning models — openly and reproducibly in `ws3`, and back a citable
peer-reviewed paper, so the field can stop rediscovering the
dynamic-inconsistency trap.

## Reference

Daugherty, P. J. (1991). *Credibility of Long Term Forest Planning: Dynamic
Inconsistency in Linear Programming Based Forest Planning Models.* PhD
thesis, University of California, Berkeley. (Archival hard copy only; not
publicly downloadable. A scanned copy is held locally — not tracked in this
repo.)

## v0.1.0a1 Definition of Done (summary)

The Daugherty (1991) modelling stack reproduced in ws3: the open-loop
harvest-scheduling LP (Model I and Model II), the sequential-replanning
simulator with inconsistency measurement, the consistent-solution
(subgame-perfect) construct, and the case-study experiments (initial forest
conditions x harvest policies x interest rates), validated against the
thesis; plus a ws3 Model II formulation, docs, CI, and a release. See
`planning/v0.1.0a1-plan.md` for the full list.

## Out of Scope

For the v0.1.x core: new science beyond Daugherty (1991) (the core paper
repeats the thesis's premise -> model -> results -> conclusion with an open
stack); any change to `fresh-fuchs` itself; recourse/rolling-horizon "fixes"
(they change the object of study). The v0.2.0 expansion (P9–P13) deliberately
extends beyond the thesis; each extension is still evaluated against the
unmodified core grid as control.
