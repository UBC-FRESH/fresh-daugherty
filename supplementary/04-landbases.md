# 04 — Per-landbase detail

Occurrence/magnitude by initial forest condition (thesis Table 5.5;
landbase definitions: `src/fresh_daugherty/instance/landbases.py`).

## All cells (including the NHF control)

| landbase | occurrence | mean_abs_rel_deviation |
| --- | --- | --- |
| 1.0 | 0.792 | 0.114 |
| 2.0 | 0.458 | 0.09 |
| 3.0 | 0.833 | 0.147 |
| 4.0 | 0.5 | 0.11 |
| 5.0 | 0.875 | 0.13 |
| 6.0 | 0.542 | 0.114 |
| 7.0 | 0.875 | 0.125 |
| 8.0 | 0.708 | 0.137 |
| 9.0 | 0.667 | 0.105 |
| 10.0 | 0.625 | 0.104 |
| 11.0 | 0.542 | 0.09 |
| 12.0 | 0.458 | 0.088 |
| 13.0 | 0.458 | 0.087 |
| 14.0 | 0.458 | 0.09 |
| 15.0 | 0.458 | 0.089 |
| 16.0 | 0.542 | 0.096 |
| 17.0 | 0.625 | 0.1 |
| 18.0 | 0.542 | 0.094 |

## Flow-constrained cells only

| landbase | occurrence | mean_abs_rel_deviation |
| --- | --- | --- |
| 1.0 | 0.9 | 0.121 |
| 2.0 | 0.5 | 0.092 |
| 3.0 | 0.95 | 0.164 |
| 4.0 | 0.55 | 0.112 |
| 5.0 | 1.0 | 0.137 |
| 6.0 | 0.6 | 0.118 |
| 7.0 | 1.0 | 0.135 |
| 8.0 | 0.8 | 0.143 |
| 9.0 | 0.7 | 0.086 |
| 10.0 | 0.65 | 0.087 |
| 11.0 | 0.55 | 0.078 |
| 12.0 | 0.45 | 0.074 |
| 13.0 | 0.45 | 0.075 |
| 14.0 | 0.45 | 0.076 |
| 15.0 | 0.45 | 0.075 |
| 16.0 | 0.55 | 0.082 |
| 17.0 | 0.65 | 0.088 |
| 18.0 | 0.55 | 0.082 |

## Construction assumptions

The thesis describes the landbases in words (pp. 78-80, Table 5.5); every
choice it leaves open is recorded in `LANDBASE_ASSUMPTIONS`:

- Landbase 1 (all mature) splits the 10,000 ac evenly across the five mature vegetation types (Table 5.4); the thesis does not give the split.
- Landbase 2 is landbase 1 with the CM-CE mature type excluded and the area redistributed evenly across the remaining four (p. 79).
- Landbases 3-8 are landbase 1/2 after 40 or 70 years of area-control harvest at a 100- or 70-year rotation (Table 5.5): a fixed area (total * period / rotation) per decade (p. 79: roughly one-tenth or one-seventh), taken from the highest-volume stands first (p. 79).
- Landbases 3-6: harvested area regenerates under prescriptions 1 and 2 only (p. 79: reforestation only); prescription 1 (natural regeneration) is viable only on CR-CF (p. 74), so CR-CF regenerates half to 1 and half to 2 and the other ecoclasses to 2 (split assumed).
- Landbases 7-8 (p. 79: the managed forests resulting from the scenarios of landbases 5 and 6): area harvested in the last 30 years received early cultural treatments, modelled as prescription 4 (vegetation management and precommercial thinning one period after planting, p. 73); earlier harvests regenerate as in landbases 3-6.
- Landbases 9-18 contain no CM-CE (p. 79).
- Landbase 9: half CH-CW, a quarter each CD-CP and CR-CF; equal acres in all age classes (10-120 yr); 'the most intensive prescriptions, divided equally between regimes with and without thinning' (p. 79) read as prescriptions 5 and 7 (fertilized, without/with commercial thinning) on CH-CW and CD-CP, and 4 and 6 on CR-CF, where fertilization is not available (p. 73).
- Landbase 10: the ecoclass shares and prescriptions of landbase 9 with an irregular age-class distribution (p. 79), drawn once from a uniform distribution with a fixed seed.
- Landbases 11-18: uniform random acres over (ecoclass, prescription, age class) cells, scaled so each management intensity gets equal acres on average (p. 79); one seed-fixed draw per landbase (seed 42 + id).
