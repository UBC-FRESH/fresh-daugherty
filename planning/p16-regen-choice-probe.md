# P16.5 — Regeneration-prescription choice: feasibility probe (#96)

Question (review finding S06): the thesis's Model II gives every regenerated
stratum a choice of management intensity (pp. 28–29, variables
`y_rpjk`; p. 74: the young-growth prescriptions "provide options for
regenerated (future) stands"). The reconstruction regenerates mature stands
to prescription 2 and managed stands to their own prescription. Can the choice
be added to the ws3 Model I formulation, and what would it take?

Probe: `PYTHONPATH=src python scripts/probe_p16_regen_choice.py <landbase> 15`
(one harvest action per target prescription, `harvest_rxK`, valid per
ecoclass per Table 5.2; NPV-free size probe, no flow rows).

## Size and time (horizon 15, one LP)

| Landbase | Columns, fixed regeneration | Columns, with choice | Build | Solve |
| --- | --- | --- | --- | --- |
| 1 (all mature) | 265 | 6,270 | 0.6 s | 0.1 s |
| 7 (area control) | 363 | 8,480 | 0.8 s | 0.1 s |
| 9 (young growth) | 2,394 | 58,786 | 5.9 s | 0.4 s |
| 11 (random) | 5,552 | 153,176 | 16.2 s | 1.4 s |

Model I with the choice stays solvable; the cost is tree building, repeated at
every replan of every cell. Rough estimate for one full re-run of all grids:
on the order of a day on 48 cores (about 3–4 h without the choice).

## Findings beyond size

1. **The objective cannot price the choice.** The LP objective is ecoclass net
   price x final-harvest volume (`lp._ecoclass_economics`, FEIS Table B-65).
   It has no reforestation, vegetation-management, precommercial-thinning or
   fertilization costs (thesis p. 74 lists them) and no commercial-thinning
   harvests. Offered a choice, the LP would pick the highest-yield
   prescription for free. A meaningful choice needs per-prescription costs
   and thinning flows in the objective.
2. **Data.** The FEIS yield tables in `instance/umpqua_feis.py` carry
   commercial-thinning entries (some with OCR gaps) that the model does not
   use. Per-prescription treatment costs are not in `instance/feis.py`; the
   reconstruction module has calibration values (`reconstruct.py`), not
   source data. Thesis p. 74: vegetation management, precommercial thinning
   and fertilization costs are constant across ecoclasses; reforestation cost
   varies by ecoclass.
3. **ws3 transition-parser defect.** `ForestModel.import_transitions_section`
   resets an action's stored masks at every `*CASE` block
   (`flush_transitions`: `self.transitions[acode] = {}`), so development types
   created later only see the last `*CASE` block of that action. The
   production model is unaffected because its last `harvest` block,
   `? ? ? regenerated baseline`, covers every development type created during a
   solve; the probe works around it with one `*CASE` per action. The fix belongs
   in ws3 (reuse boundary).
4. **Code touch points.** Flow rows and realized-volume reads key on the
   literal action `"harvest"` (`lp.py` `coeff_c_hv`/`coeff_c_rv`,
   `replan.py` product compiles); all would move to `is_harvest`.

## Options (decision gate)

- **A. Thesis-faithful intensity choice:** per-prescription costs and
  commercial thinnings in the objective (data extraction from the FEIS scans,
  or documented reconstruction values), one harvest action per target
  prescription, ws3 parser fix or workaround, code moved to `is_harvest`;
  then a full re-run. A phase of its own.
- **B. Disclose:** regeneration prescription fixed, no treatment costs, no
  commercial thinning; the thesis's management-intensity channel (its
  combination sets 3–8) and its thinning-termination inconsistency (p. 123)
  cannot arise in the reproduction.
- **C. Costs without choice:** add reforestation and treatment costs (and
  thinning flows) for the fixed regeneration path, which changes harvest-timing
  incentives, without the choice.
