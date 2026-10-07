"""P19.2 round-5 audit analyses (issue #119).

Every number the manuscript takes from the final referee audit, recomputed
from tracked records only and written to ``results/analysis/p19_round5/``.
Basis: the thesis's observation window, periods 2-11, unless a table says
otherwise. One tracked command:

    PYTHONPATH=src python scripts/analyze_p19_round5.py

Tables:

- T1 replan diagnostics (objective gap) by institution, flow-constrained and
  flow-unconstrained (NHF), with first-deviation gaps and the extension grids'
  replan statuses and floor loosening.
- T2 paired CM-CE comparison: landbases 1, 3, 5, 7 against 2, 4, 6, 8 (which
  are the same forests without CM-CE) on all 80 flow-constrained pairs.
- T3 exact-tail departures: scenarios under a fixed horizon with carried flow
  history whose realized harvest departs from the announced plan.
- T4 occurrence by institution at zero and positive rates.
- T5 the model's own highest-PNV rotations vs the thesis's Table 5.3.
- T6 revenue-denominated NDY: per-period volume ratios of the projected plan.
- T7 terminal-rotation sensitivity (core institution, terminal targets at the
  model's own highest-PNV rotations) vs the core grid, when its records exist.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fresh_daugherty.replan import is_material_relaxation

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p19_round5")
KEYS = ["landbase", "discount_rate", "flow_policy"]
INST = ["horizon_institution", "flow_history"]
WINDOW = (2, 11)
WITH_CMCE = (1, 3, 5, 7)
IV = "thesis_volume_inconsistency_2_11"


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


def _win(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.period.between(*WINDOW)]


def _status_shares(g: pd.DataFrame) -> dict:
    return {
        "replans": len(g),
        "optimal": round((g.tail_status == "optimal").mean(), 4),
        "suboptimal": round((g.tail_status == "suboptimal").mean(), 4),
        "infeasible": round((g.tail_status == "infeasible").mean(), 4),
    }


def t1_diagnostics() -> None:
    gaps = _win(pd.read_csv(RESULTS / "grid_institutions_gaps.csv"))
    rows = []
    for (h, f), g in gaps.groupby(INST):
        for label, sub in (
            ("flow-constrained", g[g.flow_policy != "NHF"]),
            ("NHF", g[g.flow_policy == "NHF"]),
        ):
            row = {"institution": f"{h}/{f}", "policies": label, **_status_shares(sub)}
            if f == "carried" and label == "flow-constrained":
                note = sub.solver_note.astype(str)
                row["material_loosening"] = round(note.map(is_material_relaxation).mean(), 4)
            rows.append(row)
    _md(pd.DataFrame(rows).set_index("institution"), OUT / "t1a_replan_status_by_institution")

    core = gaps[(gaps.horizon_institution == "rolling") & (gaps.flow_history == "reset")].copy()
    rows = []
    for (rate, nhf), g in core.groupby(["discount_rate", core.flow_policy == "NHF"]):
        rows.append(
            {
                "discount_rate": rate,
                "policies": "NHF" if nhf else "flow-constrained",
                **_status_shares(g),
            }
        )
    _md(pd.DataFrame(rows).set_index("discount_rate"), OUT / "t1b_core_replan_status_by_rate")

    lb1 = core[(core.landbase == 1) & core.flow_policy.isin(["NDY", "NHF"])]
    t = (
        lb1.groupby(["flow_policy", "discount_rate"])
        .tail_status.apply(lambda s: int((s != "optimal").sum()))
        .unstack()
    )
    _md(t, OUT / "t1c_landbase1_nonoptimal_replans")

    fc = core[core.flow_policy != "NHF"].copy()
    fc["rel_gap"] = fc.objective_gap / fc.obj_free.abs()
    flagged = fc[fc.tail_status != "optimal"]
    first = flagged.sort_values("period").groupby(KEYS).head(1)
    sub = first[first.tail_status == "suboptimal"]
    summ = pd.read_csv(RESULTS / "grid_institutions.csv")
    summ = summ[
        (summ.horizon_institution == "rolling")
        & (summ.flow_history == "reset")
        & (summ.flow_policy != "NHF")
    ]
    m = summ.merge(flagged[KEYS].drop_duplicates().assign(flag=True), on=KEYS, how="left")
    m["flag"] = m.flag.fillna(False).astype(bool)
    inc = _occ(m.occurrence_2_11)
    t1d = pd.Series(
        {
            "scenarios_with_nonoptimal_replan": len(first),
            "first_deviation_infeasible": int((first.tail_status == "infeasible").sum()),
            "first_suboptimal_gap_median_pct": round(100 * sub.rel_gap.median(), 3),
            "first_suboptimal_gap_p90_pct": round(100 * sub.rel_gap.quantile(0.9), 3),
            "inconsistent_with_flag": f"{int(m[inc].flag.sum())}/{int(inc.sum())}",
            "consistent_with_flag": f"{int(m[~inc].flag.sum())}/{int((~inc).sum())}",
        },
        name="value",
    )
    _md(t1d.to_frame(), OUT / "t1d_core_first_deviation")

    rows = []
    e2 = _win(pd.read_csv(RESULTS / "grid_cap_search_gaps.csv"))
    rows.append({"grid": "E2 cap", **_status_shares(e2)})
    e3 = _win(pd.read_csv(RESULTS / "grid_value_flow_gaps.csv"))
    for d, g in e3[e3.flow_policy != "NHF"].groupby("flow_denominator"):
        rows.append({"grid": f"E3 {d}", **_status_shares(g)})
    _md(pd.DataFrame(rows).set_index("grid"), OUT / "t1e_extension_replan_status")

    e4 = _win(pd.read_csv(RESULTS / "grid_rolling_mean_gaps.csv"))
    e4 = e4[e4.anchoring == "realized-history"].copy()
    note = e4.solver_note.astype(str)
    e4["material"] = note.map(is_material_relaxation)
    rtol = note[note.str.startswith("history_rtol=")].str.split("=").str[1].astype(float)
    rtol = rtol[rtol > 1e-4]
    t = e4.groupby("discount_rate").material.mean().round(4).to_frame("material_loosening")
    t.loc["all"] = round(e4.material.mean(), 4)
    t["median_loosening_pct"] = np.nan
    t.loc["all", "median_loosening_pct"] = round(100 * rtol.median(), 3)
    t["max_loosening_pct"] = np.nan
    t.loc["all", "max_loosening_pct"] = round(100 * rtol.max(), 3)
    t["dropped"] = np.nan
    t.loc["all", "dropped"] = int(note.isin(["relaxed_floor", "dropped_flow"]).sum())
    _md(t, OUT / "t1f_e4_realized_history_loosening")


def t2_paired_cmce() -> None:
    g = pd.read_csv(RESULTS / "grid.csv")
    g = g[g.flow_policy != "NHF"]
    rows = []
    for a in WITH_CMCE:
        x = g[g.landbase == a].set_index(["discount_rate", "flow_policy"])
        y = g[g.landbase == a + 1].set_index(["discount_rate", "flow_policy"])
        d = x[IV] - y[IV]
        rows.append(
            {
                "pair": f"{a} vs {a + 1}",
                "occurrence_with": f"{int(_occ(x.occurrence_2_11).sum())}/{len(x)}",
                "occurrence_without": f"{int(_occ(y.occurrence_2_11).sum())}/{len(y)}",
                "volume_inconsistency_diff_pts": round(100 * d.mean(), 2),
                "share_higher_with": round((d > 0).mean(), 3),
                "_d": d,
            }
        )
    alld = pd.concat([r.pop("_d") for r in rows])
    n_with = sum(int(r["occurrence_with"].split("/")[0]) for r in rows)
    n_without = sum(int(r["occurrence_without"].split("/")[0]) for r in rows)
    rows.append(
        {
            "pair": "all 80 pairs",
            "occurrence_with": f"{n_with}/80",
            "occurrence_without": f"{n_without}/80",
            "volume_inconsistency_diff_pts": round(100 * alld.mean(), 2),
            "share_higher_with": round((alld > 0).mean(), 3),
        }
    )
    _md(pd.DataFrame(rows).set_index("pair"), OUT / "t2_paired_cmce")


def t3_exact_tail() -> None:
    t = pd.read_csv(RESULTS / "grid_institutions_trajectories.csv")
    t = t[(t.horizon_institution == "fixed") & (t.flow_history == "carried") & (t.period > 1)]
    t = t[t.flow_policy != "NHF"].copy()
    t["dev"] = (t.realized_mcf - t.projected_mcf).abs() / t.projected_mcf.clip(lower=1e-9)
    rows = []
    for label, sub in (("periods 2-11", _win(t)), ("periods 2-15", t)):
        mx = sub.groupby(KEYS).dev.max()
        rows.append(
            {
                "window": label,
                "scenarios": len(mx),
                "max_dev_gt_0.1pct": int((mx > 1e-3).sum()),
                "max_dev_gt_1pct": int((mx > 1e-2).sum()),
                "max_dev_gt_5pct": int((mx > 5e-2).sum()),
            }
        )
    _md(pd.DataFrame(rows).set_index("window"), OUT / "t3a_exact_tail_departures")
    mx = t.groupby(KEYS).dev.max()
    _md(mx[mx > 1e-2].round(4).to_frame("max_period_deviation"), OUT / "t3b_exact_tail_cases")


def t4_institutions_by_rate() -> None:
    s = pd.read_csv(RESULTS / "grid_institutions.csv")
    s = s[s.flow_policy != "NHF"].copy()
    s["rates"] = np.where(s.discount_rate > 0, "2-6%", "0%")
    t = (
        s.groupby([*INST, "rates"])
        .occurrence_2_11.apply(lambda x: f"{int(_occ(x).sum())}/{len(x)}")
        .unstack()
    )
    _md(t, OUT / "t4_institutions_by_rate")


def t5_rotations() -> None:
    from fresh_daugherty.instance.feis import model_lev
    from fresh_daugherty.instance.thesis import PNV_ROTATION_ANCHORS, ROTATION_RANGES

    rows = []
    for (eco, rx), anchor in PNV_ROTATION_ANCHORS.items():
        if anchor is None:
            continue
        r, lev = model_lev(eco, rx)
        rng = ROTATION_RANGES[(eco, rx)]
        rows.append(
            {
                "ecoclass": eco.value,
                "prescription": int(rx),
                "permitted": f"{rng.lo}-{rng.hi}",
                "table_5_3": anchor.optimal_rotation_yr,
                "model_optimum": r,
                "model_lev_per_ac": round(lev, 1),
            }
        )
    _md(pd.DataFrame(rows).set_index("ecoclass"), OUT / "t5_rotations")


def t6_revenue_ndy_volume() -> None:
    t = pd.read_csv(RESULTS / "grid_value_flow_trajectories.csv")
    t = t[(t.flow_denominator == "revenue") & (t.flow_policy == "NDY")].sort_values("period")
    k = ["landbase", "discount_rate"]

    def worst_decline(s: pd.Series) -> float:
        # Declines from a positive harvest only (some 0% cells harvest
        # nothing in their first periods).
        v = s.to_numpy()
        prev, nxt = v[:-1], v[1:]
        ok = prev > 1e-6
        return float((nxt[ok] / prev[ok]).min())

    ratio = t.groupby(k).projected_mcf.apply(worst_decline)
    lb1 = t[(t.landbase == 1) & (t.discount_rate == 0.04)].projected_mcf.to_numpy()
    out = pd.Series(
        {
            "landbase1_4pc_period2_over_period1": round(lb1[1] / lb1[0], 4),
            "min_ratio_from_positive_harvest": round(ratio.min(), 4),
            "p5_of_cell_minima": round(ratio.quantile(0.05), 4),
            "median_of_cell_minima": round(ratio.median(), 4),
            "escalation_only_10yr": round(1 / 1.01**10, 4),
        },
        name="value",
    )
    _md(out.to_frame(), OUT / "t6_revenue_ndy_volume_ratios")


def t7_rotation_sensitivity() -> None:
    path = RESULTS / "grid_terminal_rotation_model.csv"
    if not path.exists():
        print(f"skip T7: {path} not found")
        return
    base = pd.read_csv(RESULTS / "grid_institutions.csv")
    base = base[(base.horizon_institution == "rolling") & (base.flow_history == "reset")]
    sens = pd.read_csv(path)
    rows = []
    for label, df in (("Table 5.3 rotations (core)", base), ("model-optimal rotations", sens)):
        fc = df[df.flow_policy != "NHF"]
        nhf = df[df.flow_policy == "NHF"]
        row = {
            "terminal_rotations": label,
            "flow_constrained_2_11": f"{int(_occ(fc.occurrence_2_11).sum())}/{len(fc)}",
            "flow_constrained_1_15": f"{int(_occ(fc.occurrence).sum())}/{len(fc)}",
            "magnitude_2_11": round(fc.mean_abs_rel_deviation_2_11.mean(), 4),
            "positive_rates_2_11": (
                f"{int(_occ(fc[fc.discount_rate > 0].occurrence_2_11).sum())}"
                f"/{int((fc.discount_rate > 0).sum())}"
            ),
            "NHF_2_11": f"{int(_occ(nhf.occurrence_2_11).sum())}/{len(nhf)}",
            "volume_inconsistency_2_11": round(100 * fc[IV].mean(), 2),
        }
        for rate, g in fc.groupby("discount_rate"):
            row[f"occ_{rate:g}"] = f"{int(_occ(g.occurrence_2_11).sum())}/{len(g)}"
        rows.append(row)
    _md(pd.DataFrame(rows).set_index("terminal_rotations"), OUT / "t7a_rotation_sensitivity")
    m = base.merge(sens, on=KEYS, suffixes=("_core", "_model"))
    m = m[m.flow_policy != "NHF"]
    a, b = _occ(m.occurrence_2_11_core), _occ(m.occurrence_2_11_model)
    agree = pd.Series(
        {
            "both_inconsistent": int((a & b).sum()),
            "core_only": int((a & ~b).sum()),
            "model_only": int((~a & b).sum()),
            "both_consistent": int((~a & ~b).sum()),
        },
        name="scenarios",
    )
    _md(agree.to_frame(), OUT / "t7b_rotation_sensitivity_agreement")
    for name, df in (("core", base), ("model", sens)):
        x = df[(df.landbase == 1) & (df.flow_policy == "NDY")]
        print(
            name,
            "landbase 1 NDY magnitude by rate",
            x.set_index("discount_rate").mean_abs_rel_deviation_2_11.round(3).to_dict(),
        )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    t1_diagnostics()
    t2_paired_cmce()
    t3_exact_tail()
    t4_institutions_by_rate()
    t5_rotations()
    t6_revenue_ndy_volume()
    t7_rotation_sensitivity()
    print(f"wrote tables to {OUT}/")


if __name__ == "__main__":
    main()
