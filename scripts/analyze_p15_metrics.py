"""P15.3 metric-robustness analysis (issue #85).

Reads only tracked records (``results/experiments/grid{,_trajectories}.csv`` and
``grid_institutions{,_trajectories}.csv``) and writes tables to
``results/analysis/p15_metrics/``. One tracked command:

    PYTHONPATH=src python scripts/analyze_p15_metrics.py

Questions: (1) how does occurrence depend on the 5% tolerance? (2) how does the
thesis's own volume-inconsistency measure (eq. 5-1, p. 83: periods 2-11,
I_V = sum|H_{n,1} - H_{1,n}| / sum H_{n,1}, i.e. announced vs realized,
normalized by announced volume) compare with the thesis's distribution
(p. 92: mean 9.0%, range 1.7-29.2%, median 7.2%; p. 124: >10% in 27% and
>6% in 60% of simulations)? (3) how much of the divergence sits in the end
periods 12-15 that the thesis excluded?

The thesis-matched subset reproduces the thesis's design on the factors this
grid varies: every flow policy at 4% plus NDY at 0/2/6% (Tables 5.8, 6.1), all
landbases. The thesis's management-intensity and timing-choice variations have
no counterpart here, and it ran only some combinations per landbase.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p15_metrics")
KEYS = ["landbase", "discount_rate", "flow_policy"]
TOLERANCES = (0.02, 0.03, 0.05, 0.075, 0.10)


def _md(df: pd.DataFrame, path: Path) -> None:
    """Write a table as CSV and GitHub-flavoured markdown (no tabulate dep)."""
    df.to_csv(path.with_suffix(".csv"))
    out = df.reset_index()
    header = "| " + " | ".join(str(c) for c in out.columns) + " |"
    sep = "| " + " | ".join("---" for _ in out.columns) + " |"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in out.to_numpy()]
    path.with_suffix(".md").write_text("\n".join([header, sep, *body]) + "\n")


def _per_cell(traj: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Per-cell window metrics from a trajectory record."""
    t = traj.copy()
    p, r = t["projected_mcf"], t["realized_mcf"]
    t["d"] = (p - r).abs() / np.maximum.reduce([p.abs(), r.abs(), np.full(len(t), 1e-9)])
    t["absdev"] = (p - r).abs()

    def agg(g: pd.DataFrame) -> pd.Series:
        w = g[(g.period >= 2) & (g.period <= 11)]
        return pd.Series(
            {
                "dbar_1_15": g["d"].mean(),
                "dbar_2_11": w["d"].mean(),
                "thesis_IV_2_11": w["absdev"].sum() / w["projected_mcf"].sum(),
                "end_share_12_15": g.loc[g.period >= 12, "d"].sum() / max(g["d"].sum(), 1e-12),
            }
        )

    return t.groupby(keys).apply(agg, include_groups=False).reset_index()


def _dist(x: pd.Series) -> dict:
    return {
        "n": int(x.size),
        "mean": round(float(x.mean()), 4),
        "median": round(float(x.median()), 4),
        "min": round(float(x.min()), 4),
        "max": round(float(x.max()), 4),
        "share_gt_6pc": round(float((x > 0.06).mean()), 3),
        "share_gt_10pc": round(float((x > 0.10).mean()), 3),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    core = pd.read_csv(RESULTS / "grid.csv")
    cells = _per_cell(pd.read_csv(RESULTS / "grid_trajectories.csv"), KEYS)
    cells = cells.merge(core[[*KEYS, "mean_abs_rel_deviation"]], on=KEYS)
    assert np.allclose(cells["dbar_1_15"], cells["mean_abs_rel_deviation"])  # same metric
    fc = cells[cells.flow_policy != "NHF"]

    # T1: occurrence vs tolerance (core flow-constrained; and per institution).
    inst = pd.read_csv(RESULTS / "grid_institutions.csv")
    inst_fc = inst[inst.flow_policy != "NHF"]
    rows = {"core (rolling/reset)": fc["dbar_1_15"]}
    for (h, f), g in inst_fc.groupby(["horizon_institution", "flow_history"]):
        rows[f"{h}/{f}"] = g["mean_abs_rel_deviation"]
    t1 = pd.DataFrame(
        {
            name: {f"tol_{t:g}": round(float((x > t).mean()), 3) for t in TOLERANCES}
            for name, x in rows.items()
        }
    ).T
    _md(t1, OUT / "t1_occurrence_vs_tolerance")

    # T2: thesis volume-inconsistency measure vs the thesis's distribution.
    matched = fc[(fc.discount_rate == 0.04) | (fc.flow_policy == "NDY")]
    t2 = pd.DataFrame(
        {
            "flow-constrained, all 360 cells": _dist(fc["thesis_IV_2_11"]),
            "thesis-matched subset": _dist(matched["thesis_IV_2_11"]),
            "thesis (178 runs; pp. 92, 124)": {
                "n": 178,
                "mean": 0.090,
                "median": 0.072,
                "min": 0.017,
                "max": 0.292,
                "share_gt_6pc": 0.60,
                "share_gt_10pc": 0.27,
            },
        }
    ).T
    _md(t2, OUT / "t2_thesis_volume_inconsistency")

    # T3: occurrence and magnitude on the periods 2-11 window vs 1-15.
    t3 = pd.DataFrame(
        {
            "window": ["periods 1-15 (sensitivity)", "periods 2-11 (thesis; paper headline)"],
            "inconsistent": [int((fc.dbar_1_15 > 0.05).sum()), int((fc.dbar_2_11 > 0.05).sum())],
            "cells": [len(fc), len(fc)],
            "mean_magnitude": [round(fc.dbar_1_15.mean(), 4), round(fc.dbar_2_11.mean(), 4)],
        }
    ).set_index("window")
    _md(t3, OUT / "t3_window")

    # T4: share of the summed divergence in end periods 12-15.
    t4 = fc["end_share_12_15"].describe()[["mean", "50%", "min", "max"]].round(3).to_frame("value")
    _md(t4, OUT / "t4_end_period_share")
    cells.to_csv(OUT / "per_cell_window_metrics.csv", index=False)
    print(f"wrote tables T1-T4 to {OUT}/")


if __name__ == "__main__":
    main()
