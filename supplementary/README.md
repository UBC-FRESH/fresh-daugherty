# Supplementary material — Dynamic inconsistency in open-loop LP forest plans

This is the curated supplement for the paper. It presents the case-study
data, the validation anchors, the full experiment-grid results (the Daugherty
1991 reproduction), the objective-gap-diagnostic evidence, and the four
modelling extensions (E1–E4), with figures and tables — all generated from
the tracked experiment records by `scripts/build_supplement.py` (see
[Reproducibility](09-reproducibility.md)).

## Contents

- [Case-study data and validation anchors](01-case-study-data.md)
- [Core experiment grid (thesis reproduction)](02-core-grid.md)
- [Objective-gap diagnostic evidence](03-gap-diagnostic.md)
- [Per-landbase detail](04-landbases.md)
- [E1: Time-varying discount-rate shapes](05-extension-e1-discount-shapes.md)
- [E2: Max-harvest-cap even-flow search](06-extension-e2-cap-search.md)
- [E3: Value-denominated flow constraints](07-extension-e3-value-flow.md)
- [E4: Rolling-mean NDY](08-extension-e4-rolling-mean.md)
- [Reproducibility](09-reproducibility.md)

## Pointers

- Per-cell experiment records (CSVs): `results/experiments/` in this
  repository ([reproducibility record](../results/experiments/REPRODUCIBILITY.md)).
- Archived benchmark release (DOI): <https://doi.org/10.5281/zenodo.21981434>
- Source planning documents (public domain, HathiTrust records 002547999 and
  002439528): the 1990 Umpqua LRMP FEIS and the 1987 DEIS.
