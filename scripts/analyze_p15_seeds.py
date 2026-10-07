"""P15.6 seed-sensitivity analysis for the random landbases 11-18 (issue #88).

Reads only tracked records (``grid.csv`` and ``grid_seeds{,_trajectories}.csv``)
and writes tables to ``results/analysis/p15_seeds/``. One tracked command:

    PYTHONPATH=src python scripts/analyze_p15_seeds.py

Seed 42 is the tracked draw (control; must reproduce the core grid's landbase
11-18 cells); seeds 1042-4042 are fresh draws of the same generator.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p15_seeds")
KEYS = ["landbase", "discount_rate", "flow_policy"]


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
    s = pd.read_csv(RESULTS / "grid_seeds.csv")
    s["occ"] = s["occurrence"].astype(str) == "True"

    ctl = s[s.landbase_seed == 42].merge(core, on=KEYS, suffixes=("_seed", "_core"))
    checks = pd.DataFrame(
        {
            "check": [
                "seed-42 cells",
                "mean divergence identical to core grid",
                "occurrence identical to core grid",
            ],
            "value": [
                len(ctl),
                bool(
                    np.array_equal(ctl.mean_abs_rel_deviation_seed, ctl.mean_abs_rel_deviation_core)
                ),
                bool((ctl.occurrence_seed.astype(str) == ctl.occurrence_core.astype(str)).all()),
            ],
        }
    ).set_index("check")
    _md(checks, OUT / "t0_checks")

    fc = s[s.flow_policy != "NHF"]
    t1 = fc.groupby("landbase_seed").agg(
        inconsistent=("occ", "sum"),
        cells=("occ", "size"),
        occurrence=("occ", "mean"),
        mean_magnitude=("mean_abs_rel_deviation", "mean"),
    )
    _md(t1.round(4), OUT / "t1_flow_constrained_by_seed")

    t2 = fc.pivot_table(index="landbase_seed", columns="discount_rate", values="occ").round(3)
    _md(t2, OUT / "t2_occurrence_by_seed_rate")

    per = fc.groupby(["landbase", "landbase_seed"]).mean_abs_rel_deviation.mean().unstack()
    t3 = pd.DataFrame(
        {
            "min_over_seeds": per.min(axis=1),
            "max_over_seeds": per.max(axis=1),
            "tracked_seed_42": per[42],
        }
    ).round(4)
    _md(t3, OUT / "t3_magnitude_range_by_landbase")
    print(f"wrote tables T0-T3 to {OUT}/")


if __name__ == "__main__":
    main()
