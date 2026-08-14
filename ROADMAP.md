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
| P1 Case-study instance + open-loop LP (Model I) | TBD | `feature/p1-open-loop` | Planned |
| P2 ws3 Model II LP formulation + solve | TBD | ws3 `feature/model-ii` | Planned |
| P3 Sequential-replanning simulator + inconsistency measurement | TBD | `feature/p3-replanning` | Planned |
| P4 Consistent-solution construct + experiments | TBD | `feature/p4-consistent` | Planned |
| P5 Validation vs thesis + docs + release | TBD | `feature/p5-release` | Planned |
| P6 Paper | TBD | TBD | Planned |

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

New science beyond Daugherty (1991) (the paper repeats the thesis's
premise -> model -> results -> conclusion with an open stack); any change to
`fresh-fuchs` itself; recourse/rolling-horizon "fixes" (they change the
object of study).
