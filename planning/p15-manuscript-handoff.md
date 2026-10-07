# P15 hand-off to the manuscript (issue #89)

Numbers for the manuscript's response to the pre-submission review, each with
its tracked source. All tables regenerate via `scripts/analyze_p15_*.py`
(re-run by `scripts/build_supplement.py`); summary in
`supplementary/10-review-analyses.md`.

## Defects found and fixed in P15 (records regenerated)

| Defect | Effect | Fix / records |
| --- | --- | --- |
| `consistency_gap_replan` ignored `carry_flow_history` | none on published grids (all used reset history) | `268fa6a` + regression test |
| Bounds built from realized harvests were exact (float noise → spurious infeasibility → silent relaxation) | E4 realized-history: occurrence 99/144 → 95/144; relaxed periods 21.1% → 18.8% (6%: 31.5% → 27.0%); magnitude 0.0716 → 0.0701 | `lp.HISTORY_RTOL = 1e-6`; E4 re-run at `268fa6a` |

## Findings by review item

| Item | Finding | Numbers | Source |
| --- | --- | --- | --- |
| R02 | Measured inconsistency depends on the replanning institution; it nearly vanishes when each replan solves the exact tail problem | flow-constrained occurrence: rolling/reset (core) 263/360 (73%); fixed/reset 219/360 (61%); rolling/carried 138/360 (38%); fixed/carried 6/360 (1.7%; 3 cells at 0% ties, 3 at 6% with relaxations). Tails optimal: 98.9% (fixed/carried) vs 27.1% (core) | `p15_institutions/t1`, `t5`, `t6` |
| R02 | Null test: fixed horizon + carried history reproduces the plan | max rel. deviation ≤ 2e-5 on landbases 1, 3, 9; CI test | `tests/test_replan.py::test_null_replanning_reproduces_the_plan` |
| R12 | Shrinking-horizon comparison archived | landbase 1, NDY, 4%: rolling/reset 0.0744; fixed/reset 0.0501; rolling/carried 0.0198; fixed/carried 0.0000 | `p15_institutions/t7` |
| R13 | Model rebuild from the realized state preserves the relevant state | null test passes on mature, area-control and intensively managed young-growth landbases | as R02 |
| R03 | NHF control is not tie-breaking at low rates | NHF tails optimal: 0% 0.425, 2% 0.667, 4–6% 1.0; 27/72 NHF cells with a gap ≥ 1% of NPV; NHF occurrence 27/72 (rolling) vs 4/72 (fixed horizon) | `p15_gaps/t1`, `t3`; `p15_institutions/t2` |
| R04 | First deviation is small in NPV terms; gap-based vs metric-based occurrence differ | first suboptimal deviation median 0.15% of NPV (p90 3.1%); gap-based occurrence 358/360 (materiality ≤ 0.1%), 348/360 (1%) vs metric 263/360 | `p15_gaps/t2`, `t3`, `t4` |
| R05 | Occurrence depends on the tolerance; ranking robust | core 2/3/5/7.5/10%: 0.956/0.900/0.731/0.592/0.467; fixed/carried ≤ 0.064 at every tolerance | `p15_metrics/t1` |
| R05/R06 | Thesis's own measure (eq. 5-1, periods 2–11) on the thesis-matched subset matches its central tendency | n=144: mean 0.082 (thesis 0.090), median 0.068 (0.072), >6% 0.611 (0.60), >10% 0.146 (0.27) | `p15_metrics/t2` |
| R08 | Horizon window | periods 2–11: 250/360 inconsistent vs 263/360 (1–15); periods 12–15 carry mean 48% of summed divergence. Terminal constraints were **not** used (experimental, known issue) | `p15_metrics/t3`, `t4`; `lp.py` docstring |
| R07 | Negatively valued strata contribute | core paired landbases 77/80 vs 51/80; E3 revenue 58/80 vs 56/80 | `p15_descriptives/t1` |
| R10 | Occurrence rises over positive rates | 42/90 (2%), 54/90 (4%), 77/90 (6%); magnitude 0.067, 0.077, 0.110 (0%: 90/90, 0.216) | `p15_descriptives/t2` |
| R16 | Disequilibrium claim needs qualifying | landbase 2 magnitude 0.082 < young-growth 0.088–0.106 | `p15_descriptives/t3` |
| R09 | E2 cap vs *realized* NDY | median total volume −0.5% (vs announced −11.5%); NPV −4.6% (positive rates −3% to −7%; 0% +10%); landbase 1, 4%: volume −1%, NPV −4%; 2/72 cells with a single period > 5% | `p15_descriptives/t4`, `t4b`; `grid_cap_search.csv` |
| R14 | Random landbases robust in magnitude; tracked draw lowest occurrence | occurrence 0.681 (seed 42) to 0.788; magnitude 0.098–0.105; spread largest at 4% (0.50–0.75) | `p15_seeds/t1`, `t2` |

## Interpretation note for the authors

The institution result reframes what the core grid measures: with a fixed
terminal date and the flow promise inherited, the open-loop plan is followed
(Bellman's principle); the inconsistency arises when each future planner
re-solves over an extended horizon with a fresh flow constraint — the thesis's
own setting (FORPLAN practice; thesis p. 82 defines inconsistency "when the
planning horizon is rolled forward and the problem updated and re-solved") and
consistent with its carried-history experiment (p. 120: volume inconsistency
averaged 1.9%). How to present this is an author decision.
