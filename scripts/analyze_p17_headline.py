"""P17.6 (#107): the paper's headline numbers on both bases.

The headline basis is the thesis's observation window, periods 2-11 (thesis
p. 83; ``*_2_11`` record columns), with the full horizon, periods 1-15, as a
sensitivity (end-of-horizon effects inflate it because the thesis's terminal
constraints are not imposed). Reads only tracked records and writes tables to
``results/analysis/p17_headline/``. One tracked command:

    PYTHONPATH=src python scripts/analyze_p17_headline.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p17_headline")
BASES = {
    "2-11": ("occurrence_2_11", "mean_abs_rel_deviation_2_11"),
    "1-15": ("occurrence", "mean_abs_rel_deviation"),
}
TOLERANCES = (0.02, 0.03, 0.05, 0.075, 0.10)


def _md(df: pd.DataFrame, path: Path) -> None:
    """Write a table as CSV and GitHub-flavoured markdown (no tabulate dep)."""
    df.to_csv(path.with_suffix(".csv"))
    out = df.reset_index()
    header = "| " + " | ".join(str(c) for c in out.columns) + " |"
    sep = "| " + " | ".join("---" for _ in out.columns) + " |"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in out.to_numpy()]
    path.with_suffix(".md").write_text("\n".join([header, sep, *body]) + "\n")


def _bool(s: pd.Series) -> pd.Series:
    return s.astype(str) == "True"


def _summ(df: pd.DataFrame, by: list[str] | None) -> pd.DataFrame:
    """inconsistent/n, occurrence and magnitude on both bases, grouped by ``by``."""
    rows = []
    groups = df.groupby(by) if by else [("all", df)]
    for key, g in groups:
        row = dict(zip(by, key if isinstance(key, tuple) else (key,), strict=True)) if by else {}
        row["n"] = len(g)
        for b, (occ, mag) in BASES.items():
            o = _bool(g[occ])
            row[f"inconsistent_{b}"] = int(o.sum())
            row[f"occurrence_{b}"] = round(float(o.mean()), 3)
            row[f"magnitude_{b}"] = round(float(g[mag].mean()), 4)
        rows.append(row)
    out = pd.DataFrame(rows)
    return out.set_index(by) if by else out.set_index(pd.Index(["all"]))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    core = pd.read_csv(RESULTS / "grid.csv")
    core["group"] = core.flow_policy.where(core.flow_policy == "NHF", "flow-constrained")
    fc = core[core.flow_policy != "NHF"]

    _md(_summ(core, ["group"]), OUT / "t1_core_overall")
    _md(_summ(core, ["group", "discount_rate"]), OUT / "t2_core_by_rate")
    _md(_summ(fc, ["flow_policy"]), OUT / "t3_core_by_policy")
    _md(_summ(fc, ["landbase"]), OUT / "t4_core_by_landbase")
    tol = pd.DataFrame(
        {
            b: {f"tol_{t:g}": round(float((fc[mag] > t).mean()), 3) for t in TOLERANCES}
            for b, (_o, mag) in BASES.items()
        }
    ).T
    _md(tol, OUT / "t5_core_tolerance")

    inst = pd.read_csv(RESULTS / "grid_institutions.csv")
    inst["group"] = inst.flow_policy.where(inst.flow_policy == "NHF", "flow-constrained")
    _md(
        _summ(inst, ["horizon_institution", "flow_history", "group"]),
        OUT / "t6_institutions",
    )

    _md(
        _summ(inst, ["horizon_institution", "flow_history", "group", "discount_rate"]),
        OUT / "t6b_institutions_by_rate",
    )
    pos = core[core.discount_rate > 0]
    _md(_summ(pos, ["group"]), OUT / "t1b_core_positive_rates")

    e1 = pd.read_csv(RESULTS / "grid_discount_paths.csv")
    e1["group"] = e1.flow_policy.where(e1.flow_policy == "NHF", "flow-constrained")
    _md(_summ(e1, ["discount_path", "group"]), OUT / "t7_e1_by_path")
    e2 = pd.read_csv(RESULTS / "grid_cap_search.csv")
    _md(_summ(e2, None), OUT / "t8_e2")
    e3 = pd.read_csv(RESULTS / "grid_value_flow.csv")
    e3fc = e3[e3.flow_policy != "NHF"]
    _md(_summ(e3fc, ["flow_denominator"]), OUT / "t9_e3_by_denominator")
    _md(_summ(e3fc, ["flow_denominator", "flow_policy"]), OUT / "t9b_e3_by_policy")
    rev = e3fc[e3fc.flow_denominator == "revenue"]
    t9c = pd.DataFrame(
        {
            "revenue-scored, 2-11": [
                int(_bool(rev.rev_occurrence_2_11).sum()),
                round(float(rev.rev_mean_abs_rel_deviation_2_11.mean()), 4),
            ],
            "revenue-scored, 1-15": [
                int(_bool(rev.rev_occurrence).sum()),
                round(float(rev.rev_mean_abs_rel_deviation.mean()), 4),
            ],
        },
        index=["inconsistent", "magnitude"],
    ).T
    _md(t9c, OUT / "t9c_e3_revenue_scored")
    e4 = pd.read_csv(RESULTS / "grid_rolling_mean.csv")
    _md(_summ(e4, ["anchoring"]), OUT / "t10_e4_by_anchoring")
    _md(_summ(e4, ["anchoring", "discount_rate"]), OUT / "t10b_e4_by_rate")
    seeds = pd.read_csv(RESULTS / "grid_seeds.csv")
    _md(_summ(seeds[seeds.flow_policy != "NHF"], ["landbase_seed"]), OUT / "t11_seeds")
    print(f"wrote headline tables to {OUT}/")


if __name__ == "__main__":
    main()
