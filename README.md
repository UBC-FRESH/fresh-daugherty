# fresh-daugherty

An open, transparent, and fully reproducible reproduction of the modelling
methods and case study of **Daugherty (1991)**, built on
[`ws3`](https://github.com/UBC-FRESH/ws3):

> Daugherty, P. J. (1991). *Credibility of Long Term Forest Planning: Dynamic
> Inconsistency in Linear Programming Based Forest Planning Models.* PhD
> thesis, University of California, Berkeley.

## Why this exists

Daugherty (1991) proves that linear-programming forest-planning models solved
as **open-loop** formulations admit **dynamically inconsistent** plans — plans
that fail Bellman's principle of optimality: a future planner, re-solving from
the realized state under the same goals, would not follow the plan's tail.
Such plans are not a credible basis for policy, and trade-off / shadow-price
analysis derived from them is biased.

The thesis was never published peer-reviewed and is effectively inaccessible
(archival hard copy only). As a result, the modelling trap it documents is
repeatedly rediscovered, and the literature contains many LP forest-planning
models presented (and cited) as rational dynamic-programming models that do
not satisfy the Bellman time-stationarity condition. This project reproduces
the thesis stack openly — open source, reproducible, transparent — so the
result becomes citable and the trap detectable, and backs a short
peer-reviewed paper.

## What it does

- Reproduces the Daugherty (1991) open-loop harvest-scheduling LP in ws3
  (Model I; the thesis's Model II formulation is not implemented), with the
  thesis's terminal constraints on every flow-constrained run.
- A sequential-replanning simulator that measures the occurrence and
  magnitude of dynamic inconsistency, with an objective-gap diagnostic that
  separates strictly suboptimal announced plans from alternate optima, under
  four replanning institutions (rolling or fixed horizon, reset or carried
  flow history).
- The case-study experiments across initial forest conditions, harvest
  policies (harvest-flow constraints), and interest rates, plus four
  extension experiments (declining discount rates, a calibrated harvest cap,
  a revenue-denominated flow, a rolling-mean flow). Consistent (closed-loop)
  solutions are not computed.

## Status

`v0.2.0` (phases P9-P19) is released and archived on Zenodo (concept DOI
10.5281/zenodo.21981433); it holds the records behind the manuscript
(`results/experiments/`, documented in `results/experiments/REPRODUCIBILITY.md`;
curated summaries in `supplementary/`). See `ROADMAP.md` and
`planning/v0.2.0-plan.md`.

## Quick Start

```bash
pip install -e ".[dev]"
fresh-daugherty --help
```

## Related

- [`fresh-fuchs`](https://github.com/UBC-FRESH/fresh-fuchs) — the stochastic,
  risk-aware forest landscape-planning model whose inner-LP dynamic
  inconsistency motivated this reproduction (documented in its
  `planning/dynamic-inconsistency-note.md`).
- [`ws3`](https://github.com/UBC-FRESH/ws3) — the wood-supply engine this
  reproduction is built on.

## Companion reference

The Model I/II/III formulations are documented in an accessible, citable
source (cited alongside the thesis):

> Gunn, E. A. (2007). *Models for Strategic Forest Management.* Chapter 16 in
> A. Weintraub, C. Romero, T. Bjørndal & R. Epstein (eds.), *Handbook of
> Operations Research in Natural Resources*, Springer, pp. 317-341.

Gunn (2007, pp. 331-332) cites Daugherty (1991) and describes the
dynamic-inconsistency phenomenon directly (the "declining non-declining
yield").

## License

MIT, Copyright (c) 2026 UBC FRESH Lab.
