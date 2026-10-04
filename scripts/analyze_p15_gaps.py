"""P15.4 objective-gap analysis (issue #86).

Reads only tracked records (``results/experiments/grid_institutions{,_gaps}.csv``;
the rolling/reset cells are the core grid's institution and reproduce
``grid.csv`` exactly) and writes tables to ``results/analysis/p15_gaps/``.
One tracked command:

    PYTHONPATH=src python scripts/analyze_p15_gaps.py

Questions: (1) tail-status shares by rate x policy, with the NHF control under
the same rule; (2) the *first* deviation per cell as an economic magnitude
(objective gap as a share of the subproblem NPV), since later periods are
evaluated from an off-plan state and repeat one early event; (3) gap-based
occurrence at materiality thresholds, reconciled with the metric-based count.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p15_gaps")
KEYS = ["landbase", "discount_rate", "flow_policy"]
MATERIALITY = (1e-6, 1e-4, 1e-3, 1e-2)


def _md(df: pd.DataFrame, path: Path) -> None:
    """Write a table as CSV and GitHub-flavoured markdown (no tabulate dep)."""
    df.to_csv(path.with_suffix(".csv"))
    out = df.reset_index()
    header = "| " + " | ".join(str(c) for c in out.columns) + " |"
    sep = "| " + " | ".join("---" for _ in out.columns) + " |"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in out.to_numpy()]
    path.with_suffix(".md").write_text("\n".join([header, sep, *body]) + "\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s = pd.read_csv(RESULTS / "grid_institutions.csv")
    g = pd.read_csv(RESULTS / "grid_institutions_gaps.csv")
    core = (s.horizon_institution == "rolling") & (s.flow_history == "reset")
    s = s[core].copy()
    g = g[
        (g.horizon_institution == "rolling") & (g.flow_history == "reset") & (g.period > 1)
    ].copy()
    g["rel_gap"] = g["objective_gap"] / g["obj_free"].abs()
    s["occ"] = s["occurrence"].astype(str) == "True"
    g["group"] = g["flow_policy"].where(g["flow_policy"] == "NHF", "flow-constrained")

    # T1: tail-status shares by rate, flow-constrained vs NHF control (same rule).
    t1 = pd.crosstab([g.group, g.discount_rate], g.tail_status, normalize="index").round(3)
    _md(t1, OUT / "t1_tail_status_by_group_rate")
    t1b = pd.crosstab([g.flow_policy], g.tail_status, normalize="index").round(3)
    _md(t1b, OUT / "t1b_tail_status_by_policy")

    # T2: first non-optimal period per cell and its gap as a share of NPV.
    nonopt = g[g.tail_status != "optimal"].sort_values("period")
    first = nonopt.groupby(KEYS).head(1).set_index(KEYS)
    first_rel = first["rel_gap"]
    rows = {}
    for grp, sub in first.groupby("group"):
        feas = sub[sub.tail_status == "suboptimal"]["rel_gap"]
        rows[grp] = {
            "cells_with_a_deviation": len(sub),
            "first_is_infeasible": int((sub.tail_status == "infeasible").sum()),
            "first_suboptimal_median_gap_pc_npv": round(100 * float(feas.median()), 4),
            "first_suboptimal_p90_gap_pc_npv": round(100 * float(feas.quantile(0.9)), 4),
            "first_period_median": float(sub["period"].median()),
        }
    t2 = pd.DataFrame(rows).T
    _md(t2, OUT / "t2_first_deviation")
    first_rel.rename("first_rel_gap").to_frame().join(first["tail_status"]).to_csv(
        OUT / "per_cell_first_deviation.csv"
    )

    # T3: gap-based occurrence at materiality thresholds vs metric-based occurrence.
    rows = []
    for grp in ("flow-constrained", "NHF"):
        cells = s[
            (s.flow_policy != "NHF") if grp == "flow-constrained" else (s.flow_policy == "NHF")
        ]
        gg = g[g.group == grp]
        rows.append(
            {
                "group": grp,
                "rule": "metric: mean divergence > 5%",
                "inconsistent": int(cells.occ.sum()),
                "cells": len(cells),
            }
        )
        for m in MATERIALITY:
            flag = gg[(gg.tail_status == "infeasible") | (gg.rel_gap >= m)]
            n = flag[KEYS].drop_duplicates().shape[0]
            rows.append(
                {
                    "group": grp,
                    "rule": f"gap: any period infeasible or gap >= {m:g} of NPV",
                    "inconsistent": n,
                    "cells": len(cells),
                }
            )
    _md(pd.DataFrame(rows).set_index(["group", "rule"]), OUT / "t3_gap_based_occurrence")

    # T4: reconciliation (flow-constrained): metric vs gap at 1e-3 materiality.
    gg = g[g.group == "flow-constrained"]
    flagged = gg[(gg.tail_status == "infeasible") | (gg.rel_gap >= 1e-3)][KEYS].drop_duplicates()
    fc = s[s.flow_policy != "NHF"].merge(flagged.assign(gap_flag=True), on=KEYS, how="left")
    fc["gap_flag"] = fc["gap_flag"].fillna(False).astype(bool)
    t4 = pd.crosstab(fc.occ.rename("metric_inconsistent"), fc.gap_flag.rename("gap_material_1e-3"))
    _md(t4, OUT / "t4_metric_vs_gap_reconciliation")
    print(f"wrote tables T1-T4 to {OUT}/")


if __name__ == "__main__":
    main()
