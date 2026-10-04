"""P15.2 replanning-institution analysis (issue #84).

Reads only the tracked records ``results/experiments/grid.csv`` (core control)
and ``grid_institutions{,_trajectories,_gaps}.csv`` and writes tables to
``results/analysis/p15_institutions/``. One tracked command:

    PYTHONPATH=src python scripts/analyze_p15_institutions.py

Question: how does dynamic inconsistency depend on the replanning institution
— rolling vs fixed (shrinking) horizon, and reset vs carried flow history? The
fixed/carried institution solves the exact tail of the original problem at
each replan (Bellman's principle applies), so it is the null reference.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p15_institutions")
KEYS = ["landbase", "discount_rate", "flow_policy"]
INST = ["horizon_institution", "flow_history"]


def _md(df: pd.DataFrame, path: Path) -> None:
    """Write a table as CSV and GitHub-flavoured markdown (no tabulate dep)."""
    df.to_csv(path.with_suffix(".csv"))
    out = df.reset_index()
    header = "| " + " | ".join(str(c) for c in out.columns) + " |"
    sep = "| " + " | ".join("---" for _ in out.columns) + " |"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in out.to_numpy()]
    path.with_suffix(".md").write_text("\n".join([header, sep, *body]) + "\n")


def _occ(s: pd.Series) -> pd.Series:
    return s.astype(str) == "True"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    core = pd.read_csv(RESULTS / "grid.csv")
    g = pd.read_csv(RESULTS / "grid_institutions.csv")
    gaps = pd.read_csv(RESULTS / "grid_institutions_gaps.csv")
    traj = pd.read_csv(RESULTS / "grid_institutions_trajectories.csv")
    g["occ"] = _occ(g["occurrence"])
    fc = g[g.flow_policy != "NHF"]

    # T1: flow-constrained cells by institution (n/N, magnitude, relaxations).
    t1 = fc.groupby(INST).agg(
        inconsistent=("occ", "sum"),
        cells=("occ", "size"),
        occurrence=("occ", "mean"),
        mean_magnitude=("mean_abs_rel_deviation", "mean"),
        relax_share=("relax_share", "mean"),
    )
    _md(t1.round(4), OUT / "t1_flow_constrained_by_institution")

    # T2: NHF control by institution.
    nhf = g[g.flow_policy == "NHF"]
    t2 = nhf.groupby(INST).agg(
        inconsistent=("occ", "sum"),
        cells=("occ", "size"),
        mean_magnitude=("mean_abs_rel_deviation", "mean"),
    )
    _md(t2.round(4), OUT / "t2_nhf_by_institution")

    # T3: flow-constrained occurrence by institution x rate and x policy.
    _md(
        fc.pivot_table(index=INST, columns="discount_rate", values="occ").round(3),
        OUT / "t3_occurrence_by_institution_rate",
    )
    _md(
        fc.pivot_table(index=INST, columns="flow_policy", values="occ").round(3),
        OUT / "t4_occurrence_by_institution_policy",
    )

    # T5: gap-diagnostic tail status (flow-constrained, periods > 1).
    gp = gaps[(gaps.flow_policy != "NHF") & (gaps.period > 1)]
    t5 = pd.crosstab([gp.horizon_institution, gp.flow_history], gp.tail_status, normalize="index")
    _md(t5.round(3), OUT / "t5_tail_status_by_institution")

    # T6: the residual inconsistent cells under the null institution.
    null = fc[(fc.horizon_institution == "fixed") & (fc.flow_history == "carried") & fc.occ]
    _md(
        null.set_index(KEYS)[["mean_abs_rel_deviation", "relax_share"]].round(4),
        OUT / "t6_fixed_carried_residual_cells",
    )

    # T7: landbase 1, NDY, 4% under each institution (the paper's example).
    ex = g[(g.landbase == 1) & (g.discount_rate == 0.04) & (g.flow_policy == "NDY")]
    _md(
        ex.set_index(INST)[["mean_abs_rel_deviation", "occurrence", "relax_share"]].round(4),
        OUT / "t7_landbase1_ndy_4pc",
    )

    # Checks recorded with the tables: control == core grid; period-1 invariant.
    ctl = g[(g.horizon_institution == "rolling") & (g.flow_history == "reset")]
    m = core.merge(ctl, on=KEYS, suffixes=("_core", "_ctl"))
    p1 = traj[traj.period == 1]
    checks = pd.DataFrame(
        {
            "check": [
                "rolling/reset control cells",
                "control mean divergence identical to core grid",
                "control occurrence identical to core grid",
                "period-1 invariant violations (all cells)",
            ],
            "value": [
                len(m),
                bool(np.array_equal(m.mean_abs_rel_deviation_core, m.mean_abs_rel_deviation_ctl)),
                bool((_occ(m.occurrence_core) == _occ(m.occurrence_ctl)).all()),
                int((~np.isclose(p1.projected_mcf, p1.realized_mcf, rtol=1e-6)).sum()),
            ],
        }
    ).set_index("check")
    _md(checks, OUT / "t0_checks")
    print(f"wrote tables T0-T7 to {OUT}/")


if __name__ == "__main__":
    main()
