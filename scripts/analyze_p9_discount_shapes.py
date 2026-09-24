"""E1 (P9) discount-shape analysis: regenerate all tables/figures (issue #56).

Reads only the tracked experiment records
(``results/experiments/grid.csv`` + ``grid_trajectories.csv`` for the
constant-rate control; ``grid_discount_paths{,_trajectories,_gaps}.csv`` for
the E1 cells) and writes summary tables and figures to
``results/analysis/p9_discount_shapes/``. One tracked command:

    PYTHONPATH=src python scripts/analyze_p9_discount_shapes.py

The analysis answers the E1 question — does a declining discount rate
mitigate or eliminate dynamic inconsistency? — and separates the two
channels: the structural (flow-constraint) channel, and the preference-level
(Strotz) channel that a declining rate itself introduces (detected by the
no-harvest-flow control cells, which carry no inter-period constraint).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p9_discount_shapes")

PATH_ORDER = ["linear-4pc-0pc", "linear-6pc-0pc", "invj-4pc-k1", "invj-4pc-k2"]
PATH_LABELS = {
    "linear-4pc-0pc": "linear 4%→0%",
    "linear-6pc-0pc": "linear 6%→0%",
    "invj-4pc-k1": "inv-j 4% (k=1)",
    "invj-4pc-k2": "inv-j 4% (k=2)",
}
CONTROL_LABELS = {0.0: "const 0%", 0.02: "const 2%", 0.04: "const 4%", 0.06: "const 6%"}


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
    e1 = pd.read_csv(RESULTS / "grid_discount_paths.csv")
    gaps = pd.read_csv(RESULTS / "grid_discount_paths_gaps.csv")
    core_traj = pd.read_csv(RESULTS / "grid_trajectories.csv")
    e1_traj = pd.read_csv(RESULTS / "grid_discount_paths_trajectories.csv")

    # --- T1: occurrence/magnitude by discount scheme (control + E1 paths) ---
    rows = []
    for rate, label in CONTROL_LABELS.items():
        sub = core[core.discount_rate == rate]
        fc = sub[sub.flow_policy != "NHF"]
        rows.append(
            {
                "scheme": label,
                "family": "constant (control)",
                "cells": len(sub),
                "occurrence_all": sub.occurrence.mean(),
                "occurrence_flow_constrained": fc.occurrence.mean(),
                "mean_magnitude_flow_constrained": fc.mean_abs_rel_deviation.mean(),
                "mean_total_rel_change_flow_constrained": fc.total_rel_change.mean(),
            }
        )
    for code in PATH_ORDER:
        sub = e1[e1.discount_path == code]
        fc = sub[sub.flow_policy != "NHF"]
        rows.append(
            {
                "scheme": PATH_LABELS[code],
                "family": sub.path_family.iloc[0],
                "cells": len(sub),
                "occurrence_all": sub.occurrence.mean(),
                "occurrence_flow_constrained": fc.occurrence.mean(),
                "mean_magnitude_flow_constrained": fc.mean_abs_rel_deviation.mean(),
                "mean_total_rel_change_flow_constrained": fc.total_rel_change.mean(),
            }
        )
    t1 = pd.DataFrame(rows).round(3)
    _md(t1, OUT / "t1_by_scheme")

    # --- T2: occurrence/magnitude by path x policy ---
    t2 = (
        e1.groupby(["discount_path", "flow_policy"])[["occurrence", "mean_abs_rel_deviation"]]
        .mean()
        .round(3)
        .reindex(pd.MultiIndex.from_product([PATH_ORDER, sorted(e1.flow_policy.unique())]))
        .rename(index=PATH_LABELS)
    )
    _md(t2, OUT / "t2_by_path_policy")

    # --- T3: gap-diagnostic tail-status shares by path (periods > 1) ---
    tail = gaps[gaps.period > 1]
    t3 = (
        tail.assign(cell_type=tail.flow_policy.where(tail.flow_policy == "NHF", "flow-constrained"))
        .groupby(["discount_path", "cell_type", "tail_status"])
        .size()
        .unstack(fill_value=0)
    )
    t3 = (t3.T / t3.sum(axis=1)).T.round(3).reindex(PATH_ORDER, level=0).rename(index=PATH_LABELS)
    _md(t3, OUT / "t3_tail_status_shares")

    # --- T4: the Strotz detector — NHF (no-flow) cells ---
    rows = []
    for rate, label in CONTROL_LABELS.items():
        sub = core[(core.discount_rate == rate) & (core.flow_policy == "NHF")]
        rows.append(
            {
                "scheme": label,
                "occurrence_nhf": sub.occurrence.mean(),
                "mean_magnitude_nhf": sub.mean_abs_rel_deviation.mean(),
                "genuine_share_nhf": None,  # no tracked gap records for the core grid
            }
        )
    nhf_gaps = tail[tail.flow_policy == "NHF"]
    for code in PATH_ORDER:
        sub = e1[(e1.discount_path == code) & (e1.flow_policy == "NHF")]
        g = nhf_gaps[nhf_gaps.discount_path == code]
        genuine = g.tail_status.isin(["suboptimal", "infeasible"]).mean()
        rows.append(
            {
                "scheme": PATH_LABELS[code],
                "occurrence_nhf": sub.occurrence.mean(),
                "mean_magnitude_nhf": sub.mean_abs_rel_deviation.mean(),
                "genuine_share_nhf": genuine,
            }
        )
    t4 = pd.DataFrame(rows).round(3)
    _md(t4, OUT / "t4_nhf_strotz_detector")

    # --- F1: occurrence + magnitude bars, control vs E1 paths ---
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2), sharey=False)
    x = range(len(t1))
    colours = ["0.65"] * len(CONTROL_LABELS) + ["0.25"] * len(PATH_ORDER)
    axes[0].bar(x, t1["occurrence_flow_constrained"], color=colours)
    axes[0].set_ylabel("occurrence")
    axes[0].set_ylim(0, 1.05)
    axes[1].bar(x, t1["mean_magnitude_flow_constrained"], color=colours)
    axes[1].set_ylabel("mean magnitude")
    for ax in axes:
        ax.set_xticks(list(x))
        ax.set_xticklabels(t1["scheme"], rotation=45, ha="right", fontsize=8)
    fig.suptitle("Dynamic inconsistency, flow-constrained cells (control grey; E1 paths dark)")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "f1_occurrence_magnitude_by_scheme.pdf", metadata={"CreationDate": None})
    plt.close(fig)

    # --- F2: focal trajectories (landbase 1, NDY): control 4% vs E1 paths ---
    fig, ax = plt.subplots(figsize=(7, 4))
    c = core_traj[
        (core_traj.landbase == 1)
        & (core_traj.discount_rate == 0.04)
        & (core_traj.flow_policy == "NDY")
    ]
    ax.plot(c.period, c.projected_mcf, "k--", lw=1.2, label="const 4% (projected)")
    ax.plot(c.period, c.realized_mcf, "k-", lw=1.2, label="const 4% (realized)")
    for code, marker in zip(PATH_ORDER, ["o", "s", "^", "v"], strict=True):
        d = e1_traj[
            (e1_traj.landbase == 1)
            & (e1_traj.discount_path == code)
            & (e1_traj.flow_policy == "NDY")
        ]
        ax.plot(
            d.period,
            d.realized_mcf,
            marker=marker,
            ms=3.5,
            lw=0.9,
            label=f"{PATH_LABELS[code]} (realized)",
        )
    ax.set_xlabel("period")
    ax.set_ylabel("harvest volume (MCF)")
    ax.set_title("Landbase 1, NDY: realized trajectories under declining discount paths")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "f2_landbase1_ndy_trajectories.pdf", metadata={"CreationDate": None})
    plt.close(fig)

    print(f"wrote tables T1-T4 and figures F1-F2 to {OUT}/")


if __name__ == "__main__":
    main()
