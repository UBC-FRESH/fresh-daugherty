"""E2 (P10) cap-search analysis: regenerate all tables/figures (issue #60).

Reads only the tracked experiment records
(``results/experiments/grid.csv`` + ``grid_trajectories.csv`` for the NDY
control; ``grid_cap_search{,_trajectories,_gaps}.csv`` for the E2 cells) and
writes summary tables and figures to ``results/analysis/p10_cap_search/``.
One tracked command:

    PYTHONPATH=src python scripts/analyze_p10_cap_search.py

The analysis answers the E2 question: does calibrating a max-harvest cap to
realized even flow (replacing the NDY flow link) mitigate or eliminate
dynamic inconsistency?
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p10_cap_search")


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
    core = pd.read_csv(RESULTS / "grid.csv")
    cap = pd.read_csv(RESULTS / "grid_cap_search.csv")
    gaps = pd.read_csv(RESULTS / "grid_cap_search_gaps.csv")
    core_traj = pd.read_csv(RESULTS / "grid_trajectories.csv")
    cap_traj = pd.read_csv(RESULTS / "grid_cap_search_trajectories.csv")

    ndy = core[core.flow_policy == "NDY"]

    # --- T1: by discount rate — E2 caps vs the NDY control ---
    rows = []
    for rate in sorted(cap.discount_rate.unique()):
        c = cap[cap.discount_rate == rate]
        n = ndy[ndy.discount_rate == rate]
        g = gaps[(gaps.discount_rate == rate) & (gaps.period > 1)]
        genuine = g.tail_status.isin(["suboptimal", "infeasible"]).mean()
        rows.append(
            {
                "discount_rate": rate,
                "cap_occurrence": c.occurrence.mean(),
                "cap_mean_magnitude": c.mean_abs_rel_deviation.mean(),
                "cap_converged": c.converged.mean(),
                "cap_mean_calibrated_mcf": c.calibrated_cap_mcf.mean(),
                "cap_mean_realized_cv": c.realized_cv.mean(),
                "cap_gap_subopt_or_infeas_share": genuine,
                "ndy_occurrence_control": n.occurrence.mean(),
                "ndy_mean_magnitude_control": n.mean_abs_rel_deviation.mean(),
            }
        )
    t1 = pd.DataFrame(rows).round(4)
    _md(t1, OUT / "t1_by_rate_vs_ndy")

    # --- T2: by landbase ---
    t2 = (
        cap.groupby("landbase")[
            [
                "converged",
                "occurrence",
                "mean_abs_rel_deviation",
                "calibrated_cap_mcf",
                "realized_cv",
                "iterations",
            ]
        ]
        .mean()
        .round(4)
    )
    _md(t2, OUT / "t2_by_landbase")

    # --- T3: overall ---
    g = gaps[gaps.period > 1]
    t3 = pd.DataFrame(
        [
            {
                "cells": len(cap),
                "converged": cap.converged.mean(),
                "occurrence": cap.occurrence.mean(),
                "mean_magnitude": cap.mean_abs_rel_deviation.mean(),
                "max_magnitude": cap.mean_abs_rel_deviation.max(),
                "gap_tail_optimal_share": (g.tail_status == "optimal").mean(),
                "gap_tail_suboptimal_share": (g.tail_status == "suboptimal").mean(),
                "gap_tail_infeasible_share": (g.tail_status == "infeasible").mean(),
            }
        ]
    ).round(4)
    _md(t3, OUT / "t3_overall")

    # --- F1: landbase 1 at 4% — NDY control vs calibrated cap ---
    fig, ax = plt.subplots(figsize=(7, 4))
    c = core_traj[
        (core_traj.landbase == 1)
        & (core_traj.discount_rate == 0.04)
        & (core_traj.flow_policy == "NDY")
    ]
    ax.plot(c.period, c.projected_mcf, "k--", lw=1.2, label="NDY (projected)")
    ax.plot(c.period, c.realized_mcf, "k-", lw=1.2, label="NDY (realized)")
    d = cap_traj[(cap_traj.landbase == 1) & (cap_traj.discount_rate == 0.04)]
    ax.plot(d.period, d.projected_mcf, "o--", ms=3.5, lw=0.9, label="cap (projected)")
    ax.plot(d.period, d.realized_mcf, "o-", ms=3.5, lw=0.9, label="cap (realized)")
    ax.set_xlabel("period")
    ax.set_ylabel("harvest volume (MCF)")
    ax.set_title("Landbase 1 at 4%: NDY flow link vs calibrated max-harvest cap")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "f1_landbase1_ndy_vs_cap.pdf")
    plt.close(fig)

    print(f"wrote tables T1-T3 and figure F1 to {OUT}/")


if __name__ == "__main__":
    main()
