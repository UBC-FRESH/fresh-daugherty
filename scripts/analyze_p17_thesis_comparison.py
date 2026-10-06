"""P17.6 (#107): comparisons with the thesis on matched populations.

Reads only tracked records (``grid.csv``, ``grid_institutions.csv``) and writes
tables to ``results/analysis/p17_thesis_comparison/``. One tracked command:

    PYTHONPATH=src python scripts/analyze_p17_thesis_comparison.py

The thesis's volume inconsistency (eq. 5-1, periods 2-11; the records'
``thesis_volume_inconsistency_2_11``) is compared on the thesis's own
populations, restricted to what the reproduction can run (no reduced
management-intensity or timing ranges, i.e. no combination sets 3-8):

- T1 by landbase subset (thesis Table 6.2, p. 99; design Tables 5.8 and 6.1,
  pp. 81, 91): landbases 1-6 with sets 1, 2, 9-15; landbases 7-10 with the same
  sets; landbases 11-18 with sets 2 and 11-14. The thesis's subsets also
  contain its reduced-choice runs (sets 3-8 on landbases 1-10), which have no
  counterpart here.
- T2 the thesis's carried-history test (pp. 118-120): landbases 1-10, 4%,
  sets 2 and 9-12 (the five flow policies), rolling horizon with the previous
  harvest carried vs reset. Thesis: carried mean 1.9%.
- T3 the thesis's reference run per landbase (NDY, 4%, full choices; p. 124:
  over-mature landbases 1-6 and three young-growth landbases, i.e. 7, 8 and 10,
  above 5%; landbase 9 and the random landbases below 3%; p. 125: 19% and 24% on the over-mature
  landbases with the smallest over-mature component).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p17_thesis_comparison")
IV = "thesis_volume_inconsistency_2_11"

#: Thesis combination sets (Table 5.8) reproducible here: (rate, policy).
SETS = {
    1: (0.04, "NHF"),
    2: (0.04, "NDY"),
    9: (0.04, "-10%"),
    10: (0.04, "-20%"),
    11: (0.04, "+/-10%"),
    12: (0.04, "+/-20%"),
    13: (0.02, "NDY"),
    14: (0.06, "NDY"),
    15: (0.00, "NDY"),
}
#: Thesis Table 6.2 (p. 99): n, mean, median of volume inconsistency.
THESIS_T62 = {
    "landbases 1-6 (over-mature)": (90, 0.1185, 0.096),
    "landbases 7-10 (young growth)": (48, 0.0684, 0.066),
    "landbases 11-18 (random)": (40, 0.0530, 0.052),
    "all": (178, 0.0902, 0.0715),
}


def _md(df: pd.DataFrame, path: Path) -> None:
    """Write a table as CSV and GitHub-flavoured markdown (no tabulate dep)."""
    df.to_csv(path.with_suffix(".csv"))
    out = df.reset_index()
    header = "| " + " | ".join(str(c) for c in out.columns) + " |"
    sep = "| " + " | ".join("---" for _ in out.columns) + " |"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in out.to_numpy()]
    path.with_suffix(".md").write_text("\n".join([header, sep, *body]) + "\n")


def _in_sets(df: pd.DataFrame, sets: list[int]) -> pd.DataFrame:
    keys = {SETS[s] for s in sets}
    mask = [(r, p) in keys for r, p in zip(df.discount_rate, df.flow_policy, strict=True)]
    return df[mask]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    core = pd.read_csv(RESULTS / "grid.csv")

    # T1: by landbase subset.
    groups = {
        "landbases 1-6 (over-mature)": (range(1, 7), [1, 2, 9, 10, 11, 12, 13, 14, 15]),
        "landbases 7-10 (young growth)": (range(7, 11), [1, 2, 9, 10, 11, 12, 13, 14, 15]),
        "landbases 11-18 (random)": (range(11, 19), [2, 11, 12, 13, 14]),
    }
    rows, parts = [], []
    for name, (lbs, sets) in groups.items():
        sub = _in_sets(core[core.landbase.isin(lbs)], sets)
        parts.append(sub)
        n, mean, median = THESIS_T62[name]
        rows.append(
            {
                "subset": name,
                "n": len(sub),
                "mean": round(float(sub[IV].mean()), 4),
                "median": round(float(sub[IV].median()), 4),
                "thesis_n": n,
                "thesis_mean": mean,
                "thesis_median": median,
            }
        )
    allp = pd.concat(parts)
    n, mean, median = THESIS_T62["all"]
    rows.append(
        {
            "subset": "all",
            "n": len(allp),
            "mean": round(float(allp[IV].mean()), 4),
            "median": round(float(allp[IV].median()), 4),
            "thesis_n": n,
            "thesis_mean": mean,
            "thesis_median": median,
        }
    )
    _md(pd.DataFrame(rows).set_index("subset"), OUT / "t1_by_landbase_subset")

    # T2: carried-history test.
    inst = pd.read_csv(RESULTS / "grid_institutions.csv")
    sub = _in_sets(inst[inst.landbase.between(1, 10)], [2, 9, 10, 11, 12])
    t2 = (
        sub.groupby(["horizon_institution", "flow_history"])[IV]
        .agg(["size", "mean", "median"])
        .round(4)
    )
    t2["thesis_mean"] = float("nan")
    t2.loc[("rolling", "carried"), "thesis_mean"] = 0.019
    _md(t2, OUT / "t2_carried_history_subset")

    # T3: reference run per landbase (NDY, 4%).
    ref = core[(core.flow_policy == "NDY") & (core.discount_rate == 0.04)]
    t3 = ref.set_index("landbase")[[IV, "mean_abs_rel_deviation_2_11"]].round(4)
    # p. 124: above 5% on the over-mature landbases (1-6) and on three of the
    # four young-growth landbases (7-10; landbase 9 is the exception, below 3%).
    t3["thesis_p124"] = ["<3%" if lb == 9 or lb >= 11 else ">5%" for lb in t3.index]
    _md(t3, OUT / "t3_reference_run_by_landbase")
    # T4: by harvest-flow policy on the thesis's Table 6.8 populations (p. 111):
    # NDY and the symmetric policies on landbases 1-18, the bounded-decline
    # policies on landbases 1-10, all at 4% with full choices.
    t68 = {
        "NDY": (0.060, 0.034),
        "-10%": (0.157, 0.192),
        "-20%": (0.161, 0.169),
        "+/-10%": (0.071, 0.046),
        "+/-20%": (0.082, 0.064),
    }
    rows = []
    for pol, (tm, tmed) in t68.items():
        lbs = range(1, 11) if pol in ("-10%", "-20%") else range(1, 19)
        sub = core[
            (core.flow_policy == pol) & (core.discount_rate == 0.04) & core.landbase.isin(lbs)
        ]
        rows.append(
            {
                "policy": pol,
                "n": len(sub),
                "mean": round(float(sub[IV].mean()), 4),
                "median": round(float(sub[IV].median()), 4),
                "thesis_mean": tm,
                "thesis_median": tmed,
            }
        )
    _md(pd.DataFrame(rows).set_index("policy"), OUT / "t4_by_policy_table_6_8")

    # T5: per landbase, mean over the thesis's full-choice sets it ran there.
    full = pd.concat(parts)
    t5 = full.groupby("landbase")[IV].agg(["size", "mean"]).round(4)
    _md(t5, OUT / "t5_by_landbase_matched_sets")
    print(f"wrote tables T1-T5 to {OUT}/")


if __name__ == "__main__":
    main()
