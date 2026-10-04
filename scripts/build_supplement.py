# ruff: noqa: RUF001
# (generated pages intentionally use en/em dashes for readability)
"""Build the curated supplementary-material tree (Phase 13 / E5, issues #67-#68).

Regenerates the whole ``supplementary/`` tree from the tracked experiment
records and typed case-study records. One tracked command:

    PYTHONPATH=src python scripts/build_supplement.py [--skip-analysis]

Every quantitative claim in the supplement traces to ``results/experiments/``
(or the typed instance records); every figure renders inline on GitHub (PNG).
By default the four extension analysis scripts are re-run first so the
supplement can never drift from the tracked records; ``--skip-analysis``
reuses the existing ``results/analysis/`` outputs.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RESULTS = Path("results/experiments")
ANALYSIS = Path("results/analysis")
SUPP = Path("supplementary")
FIGS = SUPP / "figures"

ANALYSIS_SCRIPTS = [
    "scripts/analyze_p9_discount_shapes.py",
    "scripts/analyze_p10_cap_search.py",
    "scripts/analyze_p11_value_flow.py",
    "scripts/analyze_p12_rolling_mean.py",
    "scripts/analyze_p15_institutions.py",
    "scripts/analyze_p15_metrics.py",
    "scripts/analyze_p15_gaps.py",
    "scripts/analyze_p15_descriptives.py",
    "scripts/analyze_p15_seeds.py",
]

#: (page filename, title) — the supplement's table of contents.
PAGES = [
    ("01-case-study-data.md", "Case-study data and validation anchors"),
    ("02-core-grid.md", "Core experiment grid (thesis reproduction)"),
    ("03-gap-diagnostic.md", "Objective-gap diagnostic evidence"),
    ("04-landbases.md", "Per-landbase detail"),
    ("05-extension-e1-discount-shapes.md", "E1: Time-varying discount-rate shapes"),
    ("06-extension-e2-cap-search.md", "E2: Max-harvest-cap even-flow search"),
    ("07-extension-e3-value-flow.md", "E3: Value-denominated flow constraints"),
    ("08-extension-e4-rolling-mean.md", "E4: Rolling-mean NDY"),
    ("09-reproducibility.md", "Reproducibility"),
    (
        "10-review-analyses.md",
        "Review analyses: replanning institution, robustness, gap diagnostic",
    ),
]


def _md_table(df: pd.DataFrame) -> str:
    """Render a DataFrame as a GitHub-flavoured markdown table."""
    out = df.reset_index(drop=True)
    header = "| " + " | ".join(str(c) for c in out.columns) + " |"
    sep = "| " + " | ".join("---" for _ in out.columns) + " |"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in out.to_numpy()]
    return "\n".join([header, sep, *body])


def _write(name: str, content: str) -> None:
    (SUPP / name).write_text(content.rstrip() + "\n")


def _pdf_to_png(pdf: Path, png_name: str) -> str:
    """Convert an analysis PDF figure into ``supplementary/figures/`` as PNG
    (GitHub renders PNG inline, not PDF). Returns the relative figure path."""
    FIGS.mkdir(parents=True, exist_ok=True)
    png = FIGS / png_name
    stem = png.with_suffix("")
    subprocess.run(
        ["pdftoppm", "-png", "-r", "150", "-singlefile", str(pdf), str(stem)],
        check=True,
    )
    assert png.exists(), f"pdftoppm did not produce {png}"
    return f"figures/{png_name}"


def _link(path: Path, label: str) -> str:
    """A relative link from supplementary/ to a tracked file, with an
    existence check so a stale link can never be committed."""
    rel = Path("..") / path
    assert (SUPP / rel).resolve().exists(), f"supplement link target missing: {path}"
    return f"[{label}]({rel})"


# ---------------------------------------------------------------------------
# Figures and tables from the tracked core-grid records
# ---------------------------------------------------------------------------


def _core_figures(core_traj: pd.DataFrame) -> dict[str, str]:
    """Core-grid figures (PNG) into supplementary/figures/."""
    FIGS.mkdir(parents=True, exist_ok=True)
    out: dict[str, str] = {}

    # Declining NDY, landbase 1, 4% (paper Fig. 1, regenerated from records).
    d = core_traj[
        (core_traj.landbase == 1)
        & (core_traj.discount_rate == 0.04)
        & (core_traj.flow_policy == "NDY")
    ]
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(d.period, d.projected_mcf / 1000, "o--", ms=4, label="Open-loop plan (projected)")
    ax.plot(d.period, d.realized_mcf / 1000, "s-", ms=4, label="Sequential replanning (realized)")
    ax.set_xlabel("Planning period (10 years each)")
    ax.set_ylabel("Harvest volume (thousand MCF)")
    ax.set_title("Landbase 1 (all mature), NDY at 4%:\nthe declining non-declining yield")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGS / "core_declining_ndy.png", dpi=150, metadata={"CreationDate": None})
    plt.close(fig)
    out["declining_ndy"] = "figures/core_declining_ndy.png"
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-analysis", action="store_true")
    args = parser.parse_args()

    if not args.skip_analysis:
        for script in ANALYSIS_SCRIPTS:
            subprocess.run([sys.executable, script], check=True)

    SUPP.mkdir(parents=True, exist_ok=True)
    core = pd.read_csv(RESULTS / "grid.csv")
    core_traj = pd.read_csv(RESULTS / "grid_trajectories.csv")
    e3_gaps = pd.read_csv(RESULTS / "grid_value_flow_gaps.csv")
    e1 = pd.read_csv(RESULTS / "grid_discount_paths.csv")
    e2 = pd.read_csv(RESULTS / "grid_cap_search.csv")
    e3 = pd.read_csv(RESULTS / "grid_value_flow.csv")
    e4 = pd.read_csv(RESULTS / "grid_rolling_mean.csv")

    figs = _core_figures(core_traj)

    fc = core[core.flow_policy != "NHF"]
    nhf = core[core.flow_policy == "NHF"]
    facts = _institution_facts(core)

    # ----- README (index) ---------------------------------------------------
    toc = "\n".join(f"- [{title}]({name})" for name, title in PAGES)
    _write(
        "README.md",
        f"""# Supplementary material — Dynamic inconsistency in open-loop LP forest plans

This is the curated supplement for the paper. It presents the case-study
data, the validation anchors, the full experiment-grid results (the Daugherty
1991 reproduction), the objective-gap-diagnostic evidence, and the four
modelling extensions (E1–E4), with figures and tables — all generated from
the tracked experiment records by `scripts/build_supplement.py` (see
[Reproducibility](09-reproducibility.md)).

## Contents

{toc}

## Pointers

- Per-cell experiment records (CSVs): `results/experiments/` in this
  repository ({_link(RESULTS / "REPRODUCIBILITY.md", "reproducibility record")}).
- Archived benchmark release (DOI): <https://doi.org/10.5281/zenodo.21981434>
- Source planning documents (public domain, HathiTrust records 002547999 and
  002439528): the 1990 Umpqua LRMP FEIS and the 1987 DEIS.
""",
    )

    # ----- 01 case-study data ----------------------------------------------
    from fresh_daugherty.instance.thesis import (
        MATURE_TYPE_PNV,
        PNV_ROTATION_ANCHORS,
        Ecoclass,
        Prescription,
    )

    t54 = pd.DataFrame(
        [
            {
                "ecoclass": m.ecoclass.value,
                "vegetation_type": m.vegetation_type,
                "pnv_period1_per_ac": m.pnv_period1_per_ac,
                "pnv_period2_per_ac": m.pnv_period2_per_ac,
            }
            for m in MATURE_TYPE_PNV
        ]
    )
    t53 = pd.DataFrame(
        [
            {
                "ecoclass": eco.value,
                "prescription": rx.value,
                "max_pnv_per_ac": (a.max_pnv_per_ac if a else "N/A"),
                "optimal_rotation_yr": (a.optimal_rotation_yr if a else "N/A"),
            }
            for (eco, rx), a in sorted(
                PNV_ROTATION_ANCHORS.items(), key=lambda kv: (kv[0][0].value, kv[0][1].value)
            )
            if eco in list(Ecoclass) and rx in list(Prescription)
        ]
    )
    _write(
        "01-case-study-data.md",
        f"""# 01 — Case-study data and validation anchors

The case study reproduces the Umpqua National Forest FORPLAN model
(Daugherty 1991), built from the public-domain 1990 FEIS Appendix B yield
tables and economics, cross-checked against the 1987 DEIS (the thesis's data
vintage). Data extraction is a one-time, documented, reproducible step
(`scripts/extract_umpqua_feis.py`); the package does not depend on the
scanned sources at runtime.

## Validation anchors (thesis Tables 5.3 / 5.4)

The typed records below are the calibration targets; the tests
(`tests/test_calibration.py`, `tests/test_thesis_data.py`) assert the
reconstruction reproduces them (mature-type PNVs match Table 5.4 exactly;
managed prescriptions match Table 5.3 in sign and broad rotation range;
CM-CE is the negatively-valued stratum).

### Table 5.4 — mature-type PNVs ($/ac, 4% discount)

{_md_table(t54)}

### Table 5.3 — managed-prescription PNV anchors ($/ac, 4% discount)

{_md_table(t53)}

## Yield and economics provenance

- Yield curves: 1990 FEIS Appendix B (DFSIM Douglas-fir simulator, mountain
  hemlock from Johnson's site equations), with operational-falldown
  adjustment; CMAI culmination ages consistent with the LRMP (Table IV-3).
- Economics: FEIS Table B-65 stumpage/logging/manufacturing costs, Table
  B-66 price-diameter/pond-value relations, and per-ecoclass access (road)
  costs — the high-elevation access cost makes CM-CE negatively valued.
- Typed, provenance-stamped records: `src/fresh_daugherty/instance/`
  (`thesis.py`, `feis.py`, `reconstruct.py`, `landbases.py`).
""",
    )

    # ----- 02 core grid ------------------------------------------------------
    by_policy = (
        core.groupby("flow_policy")[["occurrence", "mean_abs_rel_deviation"]].mean().round(3)
    ).reset_index()
    by_rate = (
        core.groupby("discount_rate")[["occurrence", "mean_abs_rel_deviation"]].mean().round(3)
    ).reset_index()
    by_policy_fc = (
        fc.groupby("flow_policy")[["occurrence", "mean_abs_rel_deviation"]].mean().round(3)
    ).reset_index()

    _write(
        "02-core-grid.md",
        f"""# 02 — Core experiment grid (thesis reproduction)

432 cells: 18 landbases x 4 constant discount rates (0/2/4/6%) x 6
harvest-flow policies (Table 5.6: NHF, NDY, -10%, -20%, +/-10%, +/-20%),
each a full sequential-replanning simulation over the 15-period horizon.
Per-cell records: {_link(RESULTS / "grid.csv", "grid.csv")} and
{_link(RESULTS / "grid_trajectories.csv", "grid_trajectories.csv")}.

## Headline

- Flow-constrained cells: **{fc.occurrence.mean():.0%}** exhibit dynamic
  inconsistency (mean relative divergence > 5%).
- Flow-unconstrained (NHF) control: **{nhf.occurrence.mean():.0%}**; by
  discount rate {facts["nhf_by_rate"]}. Under a fixed horizon the control's
  divergence falls to {facts["nhf_fixed"]} (a rolling-horizon effect; see
  [03](03-gap-diagnostic.md) and [10](10-review-analyses.md)).

## The declining non-declining yield

![The declining non-declining yield]({figs["declining_ndy"]})

## Occurrence and magnitude by harvest-flow policy

{_md_table(by_policy)}

Flow-constrained policies only:

{_md_table(by_policy_fc)}

## Occurrence and magnitude by discount rate

{_md_table(by_rate)}
""",
    )

    # ----- 03 gap diagnostic -------------------------------------------------
    # Full-grid gap records exist for the volume-denominated cells of the E3
    # grid (the E3 volume cells are the core-grid policies run with the
    # diagnostic): use them as the core gap evidence.
    g = e3_gaps[e3_gaps.flow_denominator == "volume"]
    tail = g[g.period > 1]
    by_pol = tail.groupby(["flow_policy", "tail_status"]).size().unstack(fill_value=0)
    by_pol = (by_pol.T / by_pol.sum(axis=1)).T.round(3).reset_index()
    by_rate = tail.groupby(["discount_rate", "tail_status"]).size().unstack(fill_value=0)
    by_rate = (by_rate.T / by_rate.sum(axis=1)).T.round(3).reset_index()
    _write(
        "03-gap-diagnostic.md",
        f"""# 03 — Objective-gap diagnostic evidence

The gap diagnostic rules out the alternate-optima reading of the divergence:
at each replan the subproblem is solved freely and again with the period-1
harvest held to the announced plan's value; if the free objective strictly
exceeds the tail-fixed objective — or the announced value is infeasible from
the realized state — the announced tail is genuinely dynamically
inconsistent.

The full-grid gap records are the volume-denominated cells of the E3 grid
({_link(RESULTS / "grid_value_flow_gaps.csv", "grid_value_flow_gaps.csv")},
`flow_denominator == 'volume'`; identical policies/rates/landbases as the
core grid). Shares of replan periods (period > 1) by tail status:

## By harvest-flow policy

{_md_table(by_pol)}

## By discount rate

{_md_table(by_rate)}

Reading: under flow-constrained policies the announced tail is predominantly
**suboptimal** (strictly improvable) or **infeasible** (cannot even be
implemented) from the realized state — genuine inconsistency. Under NHF the
announced tail stays optimal where the control is consistent; where the control
diverges ({facts["nhf_by_rate"]}), the deviations are material
({facts["nhf_material"]} NHF scenarios with a gap of at least 1% of the
optimum, or infeasible) and mostly disappear under a fixed horizon
({facts["nhf_fixed"]}): a rolling-horizon effect rather than tie-breaking.
""",
    )

    # ----- 04 per-landbase ---------------------------------------------------
    by_lb = (
        core.groupby("landbase")[["occurrence", "mean_abs_rel_deviation"]].mean().round(3)
    ).reset_index()
    by_lb_fc = (
        fc.groupby("landbase")[["occurrence", "mean_abs_rel_deviation"]].mean().round(3)
    ).reset_index()
    from fresh_daugherty.instance.landbases import LANDBASE_ASSUMPTIONS

    assumptions = "\n".join(f"- {line}" for line in LANDBASE_ASSUMPTIONS)
    _write(
        "04-landbases.md",
        f"""# 04 — Per-landbase detail

Occurrence/magnitude by initial forest condition (thesis Table 5.5;
landbase definitions: `src/fresh_daugherty/instance/landbases.py`).

## All cells (including the NHF control)

{_md_table(by_lb)}

## Flow-constrained cells only

{_md_table(by_lb_fc)}

## Construction assumptions

The thesis describes the landbases in words (pp. 78-80, Table 5.5); every
choice it leaves open is recorded in `LANDBASE_ASSUMPTIONS`:

{assumptions}
""",
    )

    # ----- 05-08 extension pages --------------------------------------------
    _extension_pages(e1, e2, e3, e4)

    # ----- 09 reproducibility -----------------------------------------------
    repro = (RESULTS / "REPRODUCIBILITY.md").read_text()
    _write(
        "09-reproducibility.md",
        f"""# 09 — Reproducibility

## Regenerate this supplement

```bash
PYTHONPATH=src python scripts/build_supplement.py
```

This re-runs the four extension analysis scripts and rebuilds every table
and figure from the tracked records in `results/experiments/`. The experiment
grids themselves regenerate via the tracked CLI entry points below.

## Benchmark record and environment

{repro}

## Archive

The complete benchmark record is archived with a DOI:
<https://doi.org/10.5281/zenodo.21981434> (release v0.1.0b1).
""",
    )

    print(f"supplement built: {len(PAGES) + 1} pages + figures in {SUPP}/")


def _institution_facts(core: pd.DataFrame) -> dict[str, str]:
    """NHF-control facts for the page 02/03 narrative, from the records."""
    nhf = core[core.flow_policy == "NHF"].copy()
    nhf["occ"] = nhf.occurrence.astype(str) == "True"
    by_rate = ", ".join(
        f"{r:.0%}: {int(g.occ.sum())}/{len(g)}" for r, g in nhf.groupby("discount_rate")
    )
    inst = pd.read_csv(RESULTS / "grid_institutions.csv")
    fx = inst[(inst.flow_policy == "NHF") & (inst.horizon_institution == "fixed")]
    fx = fx[fx.flow_history == "reset"]
    gaps = pd.read_csv(RESULTS / "grid_institutions_gaps.csv")
    g = gaps[
        (gaps.flow_policy == "NHF")
        & (gaps.horizon_institution == "rolling")
        & (gaps.flow_history == "reset")
        & (gaps.period > 1)
    ]
    material = g[(g.tail_status == "infeasible") | (g.objective_gap >= 0.01 * g.obj_free.abs())]
    n_mat = material[["landbase", "discount_rate"]].drop_duplicates().shape[0]
    return {
        "nhf_by_rate": by_rate,
        "nhf_fixed": f"{int((fx.occurrence.astype(str) == 'True').sum())}/{len(fx)}",
        "nhf_material": f"{n_mat}/{len(nhf)}",
    }


def _extension_pages(e1, e2, e3, e4) -> None:
    """Pages 05-08: headline numbers computed from the tracked extension grids,
    links to the analysis outputs and writeups, inline PNG figures."""

    # --- E1 ---
    e1_fc = e1[e1.flow_policy != "NHF"]
    by_path = (
        e1_fc.groupby("discount_path")[["occurrence", "mean_abs_rel_deviation"]]
        .mean()
        .round(3)
        .reset_index()
    )
    nhf_e1 = e1[e1.flow_policy == "NHF"]
    core = pd.read_csv(RESULTS / "grid.csv")
    core_fc = core[core.flow_policy != "NHF"]
    const_mag = ", ".join(
        f"{r:.0%}: {m:.2f}"
        for r, m in core_fc.groupby("discount_rate").mean_abs_rel_deviation.mean().items()
    )
    core_nhf0 = core[(core.flow_policy == "NHF") & (core.discount_rate == 0.0)]
    const0_nhf = float((core_nhf0.occurrence.astype(str) == "True").mean())
    f1 = _pdf_to_png(
        ANALYSIS / "p9_discount_shapes" / "f1_occurrence_magnitude_by_scheme.pdf",
        "e1_occurrence_magnitude.png",
    )
    f2 = _pdf_to_png(
        ANALYSIS / "p9_discount_shapes" / "f2_landbase1_ndy_trajectories.pdf",
        "e1_landbase1_ndy.png",
    )
    _write(
        "05-extension-e1-discount-shapes.md",
        f"""# 05 — E1: Time-varying discount-rate shapes

Does a *declining* discount rate mitigate or eliminate dynamic
inconsistency? Paths: linear 4%->0%, linear 6%->0%, inverse-j 4% (hold 1 or
2 periods, then halve per period). Grid: 432 cells (4 paths x 18 landbases x
6 policies), each with the gap diagnostic. Records:
{_link(RESULTS / "grid_discount_paths.csv", "summary")} /
{_link(RESULTS / "grid_discount_paths_trajectories.csv", "trajectories")} /
{_link(RESULTS / "grid_discount_paths_gaps.csv", "gaps")}.
Analysis writeup: {_link(ANALYSIS / "p9_discount_shapes" / "writeup.md", "p9 writeup")}.

## Headline

Declining rates make inconsistency MORE pervasive, not less: flow-constrained
occurrence is {e1_fc.occurrence.mean():.0%} across the E1 paths, with mean
magnitude {e1_fc.mean_abs_rel_deviation.mean():.2f} (constant rates, by
rate: {const_mag}). The flow-unconstrained control under declining paths
diverges at {nhf_e1.occurrence.mean():.0%} occurrence, consistent with the
preference-level (Strotz) channel of re-applying a declining schedule from each
planner's present, but not separated here from the low-rate rolling-horizon
effect (the control at a constant 0% rate: {const0_nhf:.0%}).

![Occurrence and magnitude by discount scheme]({f1})

![Landbase 1 NDY realized trajectories under declining paths]({f2})

## Occurrence and magnitude by path (flow-constrained cells)

{_md_table(by_path)}
""",
    )

    # --- E2 ---
    f1 = _pdf_to_png(
        ANALYSIS / "p10_cap_search" / "f1_landbase1_ndy_vs_cap.pdf",
        "e2_ndy_vs_cap.png",
    )
    e2_rate = (
        e2.groupby("discount_rate")[
            ["occurrence", "mean_abs_rel_deviation", "calibrated_cap_mcf", "converged"]
        ]
        .mean()
        .round(4)
        .reset_index()
    )
    lb1_cap = float(
        e2.loc[(e2.landbase == 1) & (e2.discount_rate == 0.04), "calibrated_cap_mcf"].iloc[0]
    )
    _t = pd.read_csv(RESULTS / "grid_trajectories.csv")
    lb1_ndy = float(
        _t.loc[
            (_t.landbase == 1)
            & (_t.discount_rate == 0.04)
            & (_t.flow_policy == "NDY")
            & (_t.period == 1),
            "projected_mcf",
        ].iloc[0]
    )
    lb1_gap = 1 - lb1_cap / lb1_ndy
    e2r = pd.read_csv(ANALYSIS / "p15_descriptives" / "t4_e2_vs_realized_ndy_median.csv").set_index(
        "discount_rate"
    )
    _write(
        "06-extension-e2-cap-search.md",
        f"""# 06 — E2: Max-harvest-cap even-flow search

If the NDY flow link is replaced by a per-period max-harvest cap calibrated
by bisection until the REALIZED replanned trajectory meets an even-flow
criterion (trend, fluctuation, CV thresholds — `src/fresh_daugherty/evenflow.py`),
is the calibrated plan consistent? Grid: 72 cells (18 landbases x 4 rates).
Records: {_link(RESULTS / "grid_cap_search.csv", "summary")} /
{_link(RESULTS / "grid_cap_search_trajectories.csv", "trajectories")} /
{_link(RESULTS / "grid_cap_search_gaps.csv", "gaps")}.
Analysis writeup: {_link(ANALYSIS / "p10_cap_search" / "writeup.md", "p10 writeup")}.

## Headline

Under the calibrated caps, occurrence is {e2.occurrence.mean():.0%} across the
grid (mean divergence {e2.mean_abs_rel_deviation.mean():.3f}, max
{e2.mean_abs_rel_deviation.max():.3f} — all below the 5% tolerance), with
100% convergence; single periods can still deviate by more than 5% in
{int((e2.max_abs_rel_deviation > 0.05).sum())}/{len(e2)} scenarios. The calibrated
level on landbase 1 at 4% ({lb1_cap:,.0f} MCF/period) is {lb1_gap:.0%} below the
NDY plan's *announced* level ({lb1_ndy:,.0f}). Against what replanned NDY
actually delivers, the cap's total volume differs by
{e2r.loc["all (median)", "volume_cap_vs_realized_ndy"]:+.1%} and its NPV by
{e2r.loc["all (median)", "npv_cap_vs_realized_ndy"]:+.1%} (medians over
scenarios; per-scenario spread on page 10).

![Landbase 1 at 4%: NDY flow link vs calibrated cap]({f1})

## By discount rate

{_md_table(e2_rate)}
""",
    )

    # --- E3 ---
    vol = e3[e3.flow_denominator == "volume"]
    rev = e3[e3.flow_denominator == "revenue"]
    vol_fc = vol[vol.flow_policy != "NHF"]
    rev_fc = rev[rev.flow_policy != "NHF"]
    t4 = pd.read_csv(ANALYSIS / "p11_value_flow" / "t4_cmce_filler_channel.csv")
    t4v = t4[(t4.landbase == 1) & (t4.flow_denominator == "volume")].projected_cmce_share
    cmce_lo, cmce_hi = float(t4v.min()), float(t4v.max())
    by_denom = (
        e3[e3.flow_policy != "NHF"]
        .groupby(["flow_denominator", "flow_policy"])[["occurrence", "mean_abs_rel_deviation"]]
        .mean()
        .round(3)
        .reset_index()
    )
    f1 = _pdf_to_png(
        ANALYSIS / "p11_value_flow" / "f1_landbase1_ndy_by_denominator.pdf",
        "e3_ndy_by_denominator.png",
    )
    _write(
        "07-extension-e3-value-flow.md",
        f"""# 07 — E3: Value-denominated flow constraints

Does denominating the bounded-deviation flow constraint in undiscounted net
revenue (instead of volume) mitigate or eliminate inconsistency? Grid: 864
cells (18 landbases x 4 rates x 6 policies x 2 denominators), each with the
gap diagnostic and dual volume+revenue trajectory records. Records:
{_link(RESULTS / "grid_value_flow.csv", "summary")} /
{_link(RESULTS / "grid_value_flow_trajectories.csv", "trajectories")} /
{_link(RESULTS / "grid_value_flow_gaps.csv", "gaps")}.
Analysis writeup: {_link(ANALYSIS / "p11_value_flow" / "writeup.md", "p11 writeup")}.

> Correction (P14, issue #75): the E3 records were regenerated after a defect
> that announced the volume-denominated plan in revenue-denominated cells; the
> earlier conclusion (revenue denominating worsens inconsistency) is reversed.

## Headline

Revenue denominating MITIGATES inconsistency without eliminating it:
flow-constrained occurrence {int(rev_fc.occurrence.sum())}/{len(rev_fc)}
({rev_fc.occurrence.mean():.0%}, revenue) vs
{int(vol_fc.occurrence.sum())}/{len(vol_fc)} ({vol_fc.occurrence.mean():.0%},
volume); mean magnitude {rev_fc.mean_abs_rel_deviation.mean():.3f} vs
{vol_fc.mean_abs_rel_deviation.mean():.3f}. The effect differs by policy form
(table below): NDY and bounded decline fall sharply, symmetric bounded
deviation rises slightly. Revenue NDY drives projected CM-CE harvest to
exactly zero (vs {cmce_lo:.1%}-{cmce_hi:.1%} of projected volume under volume NDY on
landbase 1), and on the paired landbases (with vs without CM-CE) the extra
inconsistency associated with negatively valued strata disappears under
revenue denominating; inconsistency persists through the remaining strata.
See the writeup's Table T4 and paired-landbase table.

![Landbase 1 at 4%: NDY by flow-row denominator]({f1})

## Occurrence and magnitude by denominator and policy (flow-constrained)

{_md_table(by_denom)}
""",
    )

    # --- E4 ---
    by_anchor = (
        e4.groupby(["anchoring", "flow_window"])[
            ["occurrence", "mean_abs_rel_deviation", "relax_share"]
        ]
        .mean()
        .round(3)
        .reset_index()
    )
    f1 = _pdf_to_png(
        ANALYSIS / "p12_rolling_mean" / "f1_landbase1_rolling_vs_pointwise.pdf",
        "e4_rolling_vs_pointwise.png",
    )
    wp = e4[e4.anchoring == "within-plan"]
    rh = e4[e4.anchoring == "realized-history"]
    _core = pd.read_csv(RESULTS / "grid.csv")
    ndy_occ = float(
        (_core.loc[_core.flow_policy == "NDY", "occurrence"].astype(str) == "True").mean()
    )
    _write(
        "08-extension-e4-rolling-mean.md",
        f"""# 08 — E4: Rolling-mean NDY

Does flooring each period's harvest at the backwards-facing rolling 2- or
3-period mean (instead of the previous period's level) change inconsistency?
Grid: 288 cells (18 landbases x 4 rates x windows {{2, 3}} x both anchoring
readings). Records: {_link(RESULTS / "grid_rolling_mean.csv", "summary")} /
{_link(RESULTS / "grid_rolling_mean_trajectories.csv", "trajectories")} /
{_link(RESULTS / "grid_rolling_mean_gaps.csv", "gaps")}.
Analysis writeup: {_link(ANALYSIS / "p12_rolling_mean" / "writeup.md", "p12 writeup")}.

## Headline

Constraint SHAPE is not the operative margin: within-plan rolling-mean
occurrence {wp.occurrence.mean():.0%} vs pointwise NDY ({ndy_occ:.0%}). The ANCHORING
INSTITUTION is: realized-history anchoring mitigates (occurrence
{rh.occurrence.mean():.0%}, magnitude {rh.mean_abs_rel_deviation.mean():.3f})
but the floor cannot be sustained in {rh.relax_share.mean():.0%} of replan
periods (mean relax_share) — the declining-NDY mechanism as recorded
infeasibility.

![Landbase 1 at 4%: pointwise NDY vs rolling-mean readings]({f1})

## By anchoring reading and window

{_md_table(by_anchor)}
""",
    )

    # --- P15 review analyses -------------------------------------------------
    def _tab(sub: str, name: str) -> str:
        return (ANALYSIS / sub / f"{name}.md").read_text().strip()

    inst = pd.read_csv(ANALYSIS / "p15_institutions" / "t1_flow_constrained_by_institution.csv")
    inst = inst.set_index(["horizon_institution", "flow_history"])

    def _io(h: str, f: str) -> str:
        r = inst.loc[(h, f)]
        return f"{int(r.inconsistent)}/{int(r.cells)} ({r.occurrence:.0%})"

    _write(
        "10-review-analyses.md",
        f"""# 10 — Review analyses (P15)

Analyses added in response to a pre-submission review (fresh-daugherty P15,
issue #82). Every table regenerates from the tracked records via the
`scripts/analyze_p15_*.py` scripts (re-run by this builder). Records:
{_link(RESULTS / "grid_institutions.csv", "institution grid")} /
{_link(RESULTS / "grid_seeds.csv", "seed grid")}; core, E2-E4 records as in
pages 02 and 06-08.

## Replanning institution

Flow-constrained occurrence: rolling horizon + reset flow history (the core
grid) {_io("rolling", "reset")}; fixed horizon + reset {_io("fixed", "reset")};
rolling + carried {_io("rolling", "carried")}; fixed horizon + carried history
(each replan solves the exact tail of the original problem)
{_io("fixed", "carried")}. A null test (CI) confirms that fixed + carried
replanning from the plan's own state reproduces the plan.

{_tab("p15_institutions", "t1_flow_constrained_by_institution")}

NHF control by institution:

{_tab("p15_institutions", "t2_nhf_by_institution")}

Gap-diagnostic tail status by institution (flow-constrained, periods > 1):

{_tab("p15_institutions", "t5_tail_status_by_institution")}

## Occurrence threshold and evaluation window

{_tab("p15_metrics", "t1_occurrence_vs_tolerance")}

The thesis's volume-inconsistency measure (eq. 5-1, periods 2-11) against its
reported distribution:

{_tab("p15_metrics", "t2_thesis_volume_inconsistency")}

{_tab("p15_metrics", "t3_window")}

## Objective-gap diagnostic (core institution)

{_tab("p15_gaps", "t1_tail_status_by_group_rate")}

First non-optimal period per cell (gap as % of the subproblem NPV):

{_tab("p15_gaps", "t2_first_deviation")}

{_tab("p15_gaps", "t3_gap_based_occurrence")}

## Descriptives

Paired landbases with/without the negatively valued CM-CE ecoclass:

{_tab("p15_descriptives", "t1_paired_cmce_landbases")}

By discount rate (flow-constrained):

{_tab("p15_descriptives", "t2_by_rate")}

E2 calibrated cap vs the *realized* NDY path (median relative difference):

{_tab("p15_descriptives", "t4_e2_vs_realized_ndy_median")}

## Random landbases: seed sensitivity

{_tab("p15_seeds", "t1_flow_constrained_by_seed")}
""",
    )


if __name__ == "__main__":
    main()
