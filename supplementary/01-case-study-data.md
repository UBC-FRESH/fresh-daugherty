# 01 — Case-study data and validation anchors

The case study reproduces the Umpqua National Forest FORPLAN model
(Daugherty 1991), built from the public-domain 1990 FEIS Appendix B yield
tables and economics, cross-checked against the 1987 DEIS (the thesis's data
vintage). Data extraction is a one-time, documented, reproducible step
(`scripts/extract_umpqua_feis.py`); the package does not depend on the
scanned sources at runtime.

## Validation anchors (thesis Tables 5.3 / 5.4)

The typed records below are the calibration targets; the tests
(`tests/test_calibration.py`, `tests/test_thesis_data.py`) assert the
reconstruction reproduces them: managed prescriptions match Table 5.3 in
sign and broad rotation range, and CM-CE is the negatively valued stratum.
The mature-type volumes are *calibrated* to Table 5.4: each is chosen so that
the model's own discounted value (4%, price escalation, end-of-period
discounting) of harvesting the stand in period 1 equals Table 5.4's period-1
PNV (`model.mature_volume_mcf`). Volumes are flat over age, so the period-2
values are not matched exactly (table below; `model.mature_value_check`).

### Table 5.4 — mature-type PNVs ($/ac, 4% discount)

| ecoclass | vegetation_type | pnv_period1_per_ac | pnv_period2_per_ac |
| --- | --- | --- | --- |
| CH-CW | sawtimber | 7646.0 | 6167.0 |
| CH-CW | two-storied | 3468.0 | 2970.0 |
| CD-CP | sawtimber | 3421.0 | 2813.0 |
| CR-CF | sawtimber | 6582.0 | 5579.0 |
| CM-CE | sawtimber | -1042.0 | -674.0 |

### Model value of a mature harvest vs Table 5.4 ($/ac, 4%)

| ecoclass | vegetation_type | period | model_value_per_ac | table_5_4_per_ac | ratio |
| --- | --- | --- | --- | --- | --- |
| CH-CW | sawtimber | 1 | 7646.0 | 7646.0 | 1.0 |
| CH-CW | sawtimber | 2 | 5705.775 | 6167.0 | 0.925 |
| CH-CW | two-storied | 1 | 3468.0 | 3468.0 | 1.0 |
| CH-CW | two-storied | 2 | 2587.971 | 2970.0 | 0.871 |
| CD-CP | sawtimber | 1 | 3421.0 | 3421.0 | 1.0 |
| CD-CP | sawtimber | 2 | 2552.898 | 2813.0 | 0.908 |
| CR-CF | sawtimber | 1 | 6582.0 | 6582.0 | 1.0 |
| CR-CF | sawtimber | 2 | 4911.772 | 5579.0 | 0.88 |
| CM-CE | sawtimber | 1 | -1042.0 | -1042.0 | 1.0 |
| CM-CE | sawtimber | 2 | -777.585 | -674.0 | 1.154 |

### Table 5.3 — managed-prescription PNV anchors ($/ac, 4% discount)

| ecoclass | prescription | max_pnv_per_ac | optimal_rotation_yr |
| --- | --- | --- | --- |
| CD-CP | 1 | N/A | N/A |
| CD-CP | 2 | 93.0 | 90 |
| CD-CP | 3 | 58.0 | 120 |
| CD-CP | 4 | 106.0 | 90 |
| CD-CP | 5 | 110.0 | 100 |
| CD-CP | 6 | 203.0 | 110 |
| CD-CP | 7 | 229.0 | 100 |
| CH-CW | 1 | N/A | N/A |
| CH-CW | 2 | 158.0 | 90 |
| CH-CW | 3 | 123.0 | 100 |
| CH-CW | 4 | 331.0 | 80 |
| CH-CW | 5 | 469.0 | 70 |
| CH-CW | 6 | 460.0 | 90 |
| CH-CW | 7 | 619.0 | 80 |
| CM-CE | 1 | N/A | N/A |
| CM-CE | 2 | -4.0 | 150 |
| CM-CE | 3 | N/A | N/A |
| CM-CE | 4 | -150.0 | 150 |
| CM-CE | 5 | N/A | N/A |
| CM-CE | 6 | -153.0 | 150 |
| CM-CE | 7 | N/A | N/A |
| CR-CF | 1 | 65.0 | 90 |
| CR-CF | 2 | 80.0 | 100 |
| CR-CF | 3 | N/A | N/A |
| CR-CF | 4 | 44.0 | 100 |
| CR-CF | 5 | N/A | N/A |
| CR-CF | 6 | 94.0 | 120 |
| CR-CF | 7 | N/A | N/A |

## Yield and economics provenance

- Yield curves: 1990 FEIS Appendix B (DFSIM Douglas-fir simulator, mountain
  hemlock from Johnson's site equations), with operational-falldown
  adjustment; CMAI culmination ages consistent with the LRMP (Table IV-3).
  The FEIS tables start at 55-175 years; below the first tabled age each
  curve follows the cell's calibrated Chapman-Richards shape scaled to the
  first FEIS value (P18.1; effect at rotation ages:
  `results/analysis/p18_young_yields/young_age_fill.md`).
- Economics: FEIS Table B-65 stumpage/logging/manufacturing costs, Table
  B-66 price-diameter/pond-value relations, and per-ecoclass access (road)
  costs — the high-elevation access cost makes CM-CE negatively valued.
- Typed, provenance-stamped records: `src/fresh_daugherty/instance/`
  (`thesis.py`, `feis.py`, `reconstruct.py`, `landbases.py`).
