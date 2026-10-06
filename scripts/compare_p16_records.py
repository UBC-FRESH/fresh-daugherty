"""P16.6 (#97): old-vs-new comparison of the headline results after the re-run.

Reads the pre-P16 records from git history (``--old-ref``, default ``45563fa``,
the last commit before the re-run) and the current records from the working
tree, and writes ``results/analysis/p16_rerun/old_vs_new.{csv,md}``.

    PYTHONPATH=src python scripts/compare_p16_records.py [--old-ref REF] [--out DIR]

P17 (#106): ``--old-ref 7693024 --out results/analysis/p17_rerun`` compares the
P16 records with the P17 re-run (full-horizon basis).
"""

from __future__ import annotations

import argparse
import io
import subprocess
from pathlib import Path

import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p16_rerun")


def _old(ref: str, name: str) -> pd.DataFrame:
    blob = subprocess.run(
        ["git", "show", f"{ref}:{RESULTS / name}"], check=True, capture_output=True, text=True
    ).stdout
    return pd.read_csv(io.StringIO(blob))


def _occ(df: pd.DataFrame) -> pd.Series:
    return df["occurrence"].astype(str) == "True"


def _rows(df: pd.DataFrame, grid: str, group: dict[str, object] | None = None) -> list[dict]:
    d = df.copy()
    d["occ"] = _occ(d)
    for k, v in (group or {}).items():
        d = d[d[k] == v]
    out = []
    for label, sub in (
        ("flow-constrained", d[d.flow_policy != "NHF"]),
        ("NHF", d[d.flow_policy == "NHF"]),
    ):
        if len(sub):
            out.append(
                {
                    "grid": grid,
                    "subset": label,
                    "inconsistent": f"{int(sub.occ.sum())}/{len(sub)}",
                    "occurrence": round(float(sub.occ.mean()), 3),
                    "magnitude": round(float(sub.mean_abs_rel_deviation.mean()), 4),
                }
            )
    return out


def _summaries(get) -> list[dict]:
    rows = _rows(get("grid.csv"), "core")
    core = get("grid.csv")
    for r in sorted(core.discount_rate.unique()):
        rows += [
            x | {"subset": f"{x['subset']}, {r:.0%}"}
            for x in _rows(core, "core", {"discount_rate": r})
        ]
    rows += _rows(get("grid_discount_paths.csv"), "E1")
    e2 = get("grid_cap_search.csv")
    rows.append(
        {
            "grid": "E2",
            "subset": "all",
            "inconsistent": f"{int(_occ(e2).sum())}/{len(e2)}",
            "occurrence": round(float(_occ(e2).mean()), 3),
            "magnitude": round(float(e2.mean_abs_rel_deviation.mean()), 4),
        }
    )
    e3 = get("grid_value_flow.csv")
    for den in ("volume", "revenue"):
        rows += [x | {"grid": f"E3 {den}"} for x in _rows(e3[e3.flow_denominator == den], "E3")]
    e4 = get("grid_rolling_mean.csv")
    for anc in ("within-plan", "realized-history"):
        sub = e4[e4.anchoring == anc]
        rows.append(
            {
                "grid": f"E4 {anc}",
                "subset": "NDY",
                "inconsistent": f"{int(_occ(sub).sum())}/{len(sub)}",
                "occurrence": round(float(_occ(sub).mean()), 3),
                "magnitude": round(float(sub.mean_abs_rel_deviation.mean()), 4),
            }
        )
    inst = get("grid_institutions.csv")
    for (h, f), sub in inst.groupby(["horizon_institution", "flow_history"]):
        rows += [x | {"grid": f"institutions {h}/{f}"} for x in _rows(sub, "inst")]
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-ref", default="45563fa")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    out_dir = args.out
    old = pd.DataFrame(_summaries(lambda n: _old(args.old_ref, n)))
    new = pd.DataFrame(_summaries(lambda n: pd.read_csv(RESULTS / n)))
    m = old.merge(new, on=["grid", "subset"], suffixes=("_old", "_new"), how="outer")
    out_dir.mkdir(parents=True, exist_ok=True)
    m.to_csv(out_dir / "old_vs_new.csv", index=False)
    header = "| " + " | ".join(m.columns) + " |"
    sep = "| " + " | ".join("---" for _ in m.columns) + " |"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in m.to_numpy()]
    (out_dir / "old_vs_new.md").write_text("\n".join([header, sep, *body]) + "\n")
    print(f"wrote {out_dir}/old_vs_new.md ({len(m)} rows)")


if __name__ == "__main__":
    main()
