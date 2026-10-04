"""P15.5 core descriptives and E2 vs realized NDY (issue #87).

Reads only tracked records (``grid.csv``, ``grid_value_flow{,_gaps}.csv``,
``grid_cap_search{,_trajectories,_gaps}.csv``) and writes tables to
``results/analysis/p15_descriptives/``. One tracked command:

    PYTHONPATH=src python scripts/analyze_p15_descriptives.py

Tables: paired landbases with/without the negatively valued CM-CE ecoclass
(landbases 2, 4, 6, 8 are 1, 3, 5, 7 without it); occurrence and magnitude by
discount rate; per-landbase occurrence and magnitude; and the E2 calibrated cap
compared with the *realized* (not announced) NDY path on total volume and on
NPV, NPV = sum_t realized net revenue_t * (1 + r)^(-10 t) (the LP objective's
convention; revenue from the gap records).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p15_descriptives")
KEYS = ["landbase", "discount_rate", "flow_policy"]
WITH_CMCE = (1, 3, 5, 7)
WITHOUT_CMCE = (2, 4, 6, 8)


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


def _npv(gaps: pd.DataFrame, keys: list[str]) -> pd.Series:
    g = gaps.copy()
    g["pv"] = g["realized_revenue"] * (1.0 + g["discount_rate"]) ** (-10 * g["period"])
    return g.groupby(keys)["pv"].sum()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    core = pd.read_csv(RESULTS / "grid.csv")
    core["occ"] = _occ(core["occurrence"])
    fc = core[core.flow_policy != "NHF"]

    # T1: paired landbases (core, and E3 volume/revenue).
    e3 = pd.read_csv(RESULTS / "grid_value_flow.csv")
    e3["occ"] = _occ(e3["occurrence"])
    e3fc = e3[e3.flow_policy != "NHF"]
    rows = []
    for name, df in (
        ("core (volume)", fc),
        *((f"E3 {d}", e3fc[e3fc.flow_denominator == d]) for d in ("volume", "revenue")),
    ):
        a = df[df.landbase.isin(WITH_CMCE)]
        b = df[df.landbase.isin(WITHOUT_CMCE)]
        rows.append(
            {
                "grid": name,
                "with_cmce": f"{int(a.occ.sum())}/{len(a)}",
                "without_cmce": f"{int(b.occ.sum())}/{len(b)}",
                "with_magnitude": round(a.mean_abs_rel_deviation.mean(), 4),
                "without_magnitude": round(b.mean_abs_rel_deviation.mean(), 4),
            }
        )
    _md(pd.DataFrame(rows).set_index("grid"), OUT / "t1_paired_cmce_landbases")

    # T2: flow-constrained occurrence and magnitude by rate (and by policy).
    t2 = fc.groupby("discount_rate").agg(
        inconsistent=("occ", "sum"),
        cells=("occ", "size"),
        occurrence=("occ", "mean"),
        mean_magnitude=("mean_abs_rel_deviation", "mean"),
    )
    _md(t2.round(4), OUT / "t2_by_rate")
    _md(
        fc.pivot_table(index="flow_policy", columns="discount_rate", values="occ").round(3),
        OUT / "t2b_occurrence_by_policy_rate",
    )

    # T3: per-landbase occurrence and magnitude (flow-constrained).
    t3 = fc.groupby("landbase").agg(
        inconsistent=("occ", "sum"),
        cells=("occ", "size"),
        mean_magnitude=("mean_abs_rel_deviation", "mean"),
    )
    _md(t3.round(4), OUT / "t3_by_landbase")

    # T4: E2 calibrated cap vs realized NDY, volume and NPV, per (landbase, rate).
    cap = pd.read_csv(RESULTS / "grid_cap_search.csv")
    cap_gaps = pd.read_csv(RESULTS / "grid_cap_search_gaps.csv")
    ndy_gaps = pd.read_csv(RESULTS / "grid_value_flow_gaps.csv")
    ndy_gaps = ndy_gaps[(ndy_gaps.flow_denominator == "volume") & (ndy_gaps.flow_policy == "NDY")]
    ndy = core[core.flow_policy == "NDY"].set_index(["landbase", "discount_rate"])
    k2 = ["landbase", "discount_rate"]
    comp = cap.set_index(k2)[["calibrated_cap_mcf", "total_realized"]].rename(
        columns={"total_realized": "cap_total_realized_mcf"}
    )
    comp["ndy_total_announced_mcf"] = ndy["total_projected"]
    comp["ndy_total_realized_mcf"] = ndy["total_realized"]
    comp["cap_npv"] = _npv(cap_gaps, k2)
    comp["ndy_realized_npv"] = _npv(ndy_gaps, k2)
    comp["volume_cap_vs_realized_ndy"] = (
        comp.cap_total_realized_mcf / comp.ndy_total_realized_mcf - 1
    )
    comp["volume_cap_vs_announced_ndy"] = (
        comp.cap_total_realized_mcf / comp.ndy_total_announced_mcf - 1
    )
    comp["npv_cap_vs_realized_ndy"] = comp.cap_npv / comp.ndy_realized_npv - 1
    comp.round(4).to_csv(OUT / "per_cell_e2_vs_realized_ndy.csv")
    t4 = comp[
        ["volume_cap_vs_realized_ndy", "volume_cap_vs_announced_ndy", "npv_cap_vs_realized_ndy"]
    ]
    t4 = t4.groupby("discount_rate").median().round(4)
    t4.loc["all (median)"] = comp[t4.columns].median().round(4)
    _md(t4, OUT / "t4_e2_vs_realized_ndy_median")
    _md(comp.loc[[(1, 0.04)]].round(2), OUT / "t4b_e2_landbase1_4pc")
    print(f"wrote tables T1-T4 to {OUT}/")


if __name__ == "__main__":
    main()
