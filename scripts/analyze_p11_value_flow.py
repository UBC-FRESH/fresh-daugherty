"""E3 (P11) value-flow analysis: regenerate all tables/figures (issue #63).

Reads the tracked experiment records (``results/experiments/grid_value_flow*.csv``)
and writes summary tables and figures to ``results/analysis/p11_value_flow/``.
The CM-CE filler-channel test (T4) re-runs the four focal open-loop solves
(landbases 1/2 x NDY at 0%/4% x volume/revenue denominators) deterministically
from the tracked case-study data. One tracked command:

    PYTHONPATH=src python scripts/analyze_p11_value_flow.py

The analysis answers the E3 question: does denominating the bounded-deviation
flow constraint in undiscounted net revenue instead of volume mitigate or
eliminate dynamic inconsistency — and does disabling the negatively-valued
CM-CE filler channel remove it?
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RESULTS = Path("results/experiments")
OUT = Path("results/analysis/p11_value_flow")

# Regenerable model intermediates for the CM-CE solves live under the ignored
# outputs/ tree, not the tracked analysis directory.
WORK = Path("outputs") / "p11_cmce_work"


def _md(df: pd.DataFrame, path: Path) -> None:
    """Write a table as CSV and GitHub-flavoured markdown (no tabulate dep)."""
    df.to_csv(path.with_suffix(".csv"))
    out = df.reset_index()
    header = "| " + " | ".join(str(c) for c in out.columns) + " |"
    sep = "| " + " | ".join("---" for _ in out.columns) + " |"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in out.to_numpy()]
    path.with_suffix(".md").write_text("\n".join([header, sep, *body]) + "\n")


def _cmce_share(landbase: int, rate: float, denominator: str, workdir: Path) -> dict:
    """Projected CM-CE harvest volume and share in the open-loop NDY plan."""
    from fresh_daugherty.instance.landbases import landbase_areas
    from fresh_daugherty.lp import add_open_loop_problem, solve_open_loop
    from fresh_daugherty.model import (
        bootstrap_model,
        build_woodstock_sections,
        prepare_optimization,
    )

    areas = landbase_areas(landbase)
    build_woodstock_sections(workdir / "model", areas=areas)
    model = prepare_optimization(bootstrap_model(workdir / "model", horizon=15), horizon=15)
    problem = add_open_loop_problem(
        model,
        discount_rate=rate,
        flow_geometry="consecutive",
        flow_decrease=0.0,  # NDY
        flow_denominator=denominator,
    )
    df = solve_open_loop(model, problem)
    assert problem.status() == "optimal"
    cmce_dtks = [dtk for dtk in model.dtypes if str(dtk[1]) == "cmce"]
    cmce = sum(
        model.compile_product(p, "totvol", acode="harvest", dtype_keys=[dtk])
        for p in model.periods
        for dtk in cmce_dtks
    )
    total = float(df["harvest_volume_mcf"].sum())
    return {
        "landbase": landbase,
        "discount_rate": rate,
        "flow_denominator": denominator,
        "projected_total_mcf": total,
        "projected_cmce_mcf": float(cmce),
        "projected_cmce_share": float(cmce / total) if total else 0.0,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s = pd.read_csv(RESULTS / "grid_value_flow.csv")
    traj = pd.read_csv(RESULTS / "grid_value_flow_trajectories.csv")

    # --- T1: by denominator x policy ---
    t1 = (
        s.groupby(["flow_denominator", "flow_policy"])[
            ["occurrence", "mean_abs_rel_deviation", "rev_mean_abs_rel_deviation"]
        ]
        .mean()
        .round(3)
    )
    _md(t1, OUT / "t1_by_denominator_policy")

    # --- T2: by denominator x rate ---
    t2 = (
        s.groupby(["flow_denominator", "discount_rate"])[
            ["occurrence", "mean_abs_rel_deviation", "rev_mean_abs_rel_deviation"]
        ]
        .mean()
        .round(3)
    )
    _md(t2, OUT / "t2_by_denominator_rate")

    # --- T3: NHF identity check (plumbing validation) ---
    nhf = s[s.flow_policy == "NHF"]
    t3 = (
        nhf.groupby("flow_denominator")[["occurrence", "mean_abs_rel_deviation"]]
        .agg(["mean", "count"])
        .round(4)
    )
    _md(t3, OUT / "t3_nhf_identity_check")

    # --- T4: CM-CE filler-channel test (focal open-loop solves) ---
    workdir = WORK
    rows = []
    for lb in (1, 2):
        for rate in (0.0, 0.04):
            for denom in ("volume", "revenue"):
                rows.append(_cmce_share(lb, rate, denom, workdir / f"lb{lb}_r{rate}_{denom}"))
    t4 = pd.DataFrame(rows).round(4)
    _md(t4, OUT / "t4_cmce_filler_channel")

    # --- F1: landbase 1, NDY, 4%: volume- vs revenue-denominated ---
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4), sharey=False)
    for ax, denom in zip(axes, ["volume", "revenue"], strict=True):
        d = traj[
            (traj.landbase == 1)
            & (traj.discount_rate == 0.04)
            & (traj.flow_policy == "NDY")
            & (traj.flow_denominator == denom)
        ]
        ax.plot(d.period, d.projected_mcf, "k--", lw=1.2, label="projected (volume)")
        ax.plot(d.period, d.realized_mcf, "k-", lw=1.2, label="realized (volume)")
        ax.set_title(f"{denom}-denominated NDY")
        ax.set_xlabel("period")
        axes[0].set_ylabel("harvest volume (MCF)")
        ax.legend(fontsize=8)
    fig.suptitle("Landbase 1 at 4%: NDY by flow-row denominator")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "f1_landbase1_ndy_by_denominator.pdf")
    plt.close(fig)

    print(f"wrote tables T1-T4 and figure F1 to {OUT}/")


if __name__ == "__main__":
    main()
