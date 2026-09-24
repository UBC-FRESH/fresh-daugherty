"""E4 (P12) rolling-mean NDY analysis: regenerate all tables/figures (issue #66).

Reads only the tracked experiment records
(``results/experiments/grid.csv`` + ``grid_trajectories.csv`` for the
pointwise-NDY control; ``grid_rolling_mean{,_trajectories,_gaps}.csv`` for the
E4 cells) and writes summary tables and figures to
``results/analysis/p12_rolling_mean/``. One tracked command:

    PYTHONPATH=src python scripts/analyze_p12_rolling_mean.py

The analysis answers the E4 question: does flooring each period's harvest at
the backwards-facing rolling 2- or 3-period mean (instead of the previous
period's level) change dynamic-inconsistency behaviour — and how much of the
effect is the anchoring institution (within-plan vs realized-history windows)?
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p12_rolling_mean")


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
    rm = pd.read_csv(RESULTS / "grid_rolling_mean.csv")
    gaps = pd.read_csv(RESULTS / "grid_rolling_mean_gaps.csv")
    core_traj = pd.read_csv(RESULTS / "grid_trajectories.csv")
    rm_traj = pd.read_csv(RESULTS / "grid_rolling_mean_trajectories.csv")

    ndy = core[core.flow_policy == "NDY"]

    # --- T1: by anchoring x window (vs the pointwise-NDY control) ---
    t1 = (
        rm.groupby(["anchoring", "flow_window"])[
            ["occurrence", "mean_abs_rel_deviation", "relax_share", "total_rel_change"]
        ]
        .mean()
        .round(3)
    )
    _md(t1, OUT / "t1_by_anchoring_window")

    # --- T2: by anchoring x rate ---
    t2 = (
        rm.groupby(["anchoring", "discount_rate"])[
            ["occurrence", "mean_abs_rel_deviation", "relax_share"]
        ]
        .mean()
        .round(3)
    )
    _md(t2, OUT / "t2_by_anchoring_rate")

    # --- T3: gap tail-status shares by anchoring (periods > 1) ---
    tail = gaps[gaps.period > 1]
    t3 = tail.groupby(["anchoring", "tail_status"]).size().unstack(fill_value=0)
    t3 = (t3.T / t3.sum(axis=1)).T.round(3)
    _md(t3, OUT / "t3_tail_status_by_anchoring")

    # --- control reference row (pointwise NDY from the core grid) ---
    ctrl = pd.DataFrame(
        [
            {
                "policy": "NDY (pointwise, within-plan) — core control",
                "occurrence": ndy.occurrence.mean(),
                "mean_magnitude": ndy.mean_abs_rel_deviation.mean(),
            },
            {
                "policy": "rolling-mean NDY (within-plan) — E4",
                "occurrence": rm[rm.anchoring == "within-plan"].occurrence.mean(),
                "mean_magnitude": rm[rm.anchoring == "within-plan"].mean_abs_rel_deviation.mean(),
            },
            {
                "policy": "rolling-mean NDY (realized-history) — E4",
                "occurrence": rm[rm.anchoring == "realized-history"].occurrence.mean(),
                "mean_magnitude": rm[
                    rm.anchoring == "realized-history"
                ].mean_abs_rel_deviation.mean(),
            },
        ]
    ).round(3)
    _md(ctrl, OUT / "t4_control_comparison")

    # --- F1: landbase 1 at 4%: pointwise NDY vs rolling-mean readings ---
    fig, ax = plt.subplots(figsize=(7, 4))
    c = core_traj[
        (core_traj.landbase == 1)
        & (core_traj.discount_rate == 0.04)
        & (core_traj.flow_policy == "NDY")
    ]
    ax.plot(c.period, c.projected_mcf, "k--", lw=1.2, label="NDY (projected)")
    ax.plot(c.period, c.realized_mcf, "k-", lw=1.2, label="NDY (realized)")
    for anch, marker, lbl in (
        ("within-plan", "o", "rolling k=2 within-plan (realized)"),
        ("realized-history", "s", "rolling k=2 realized-history (realized)"),
    ):
        d = rm_traj[
            (rm_traj.landbase == 1)
            & (rm_traj.discount_rate == 0.04)
            & (rm_traj.flow_window == 2)
            & (rm_traj.anchoring == anch)
        ]
        ax.plot(
            d.period,
            d.realized_mcf,
            marker=marker,
            ms=3.5,
            lw=0.9,
            label=lbl,
        )
    ax.set_xlabel("period")
    ax.set_ylabel("harvest volume (MCF)")
    ax.set_title("Landbase 1 at 4%: pointwise NDY vs rolling-mean NDY readings")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "f1_landbase1_rolling_vs_pointwise.pdf", metadata={"CreationDate": None})
    plt.close(fig)

    print(f"wrote tables T1-T4 and figure F1 to {OUT}/")


if __name__ == "__main__":
    main()
