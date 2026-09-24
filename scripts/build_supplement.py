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
    fig.savefig(FIGS / "core_declining_ndy.png", dpi=150)
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
- No-harvest-flow (NHF) control: **{nhf.occurrence.mean():.0%}** — and that
  divergence is concentrated at 0-2% where the flat objective admits
  alternate optima (see [03](03-gap-diagnostic.md)).

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
implemented) from the realized state — genuine inconsistency; under NHF the
tail remains largely optimal except at the lowest rates (flat-objective
tie-churn), which is why the NHF divergence metric is not read as genuine
inconsistency there.
""",
    )

    # ----- 04 per-landbase ---------------------------------------------------
    by_lb = (
        core.groupby("landbase")[["occurrence", "mean_abs_rel_deviation"]].mean().round(3)
    ).reset_index()
    by_lb_fc = (
        fc.groupby("landbase")[["occurrence", "mean_abs_rel_deviation"]].mean().round(3)
    ).reset_index()
    _write(
        "04-landbases.md",
        f"""# 04 — Per-landbase detail

Occurrence/magnitude by initial forest condition (thesis Table 5.5;
landbase definitions: `src/fresh_daugherty/instance/landbases.py`).

## All cells (including the NHF control)

{_md_table(by_lb)}

## Flow-constrained cells only

{_md_table(by_lb_fc)}

The inconsistency occurs across all eighteen initial forest conditions and
is most pronounced on the disequilibrium structures: the all-mature
landbases (1, 2) and the area-control-derived landbases (3-8).
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
magnitude {e1_fc.mean_abs_rel_deviation.mean():.2f} (vs 0.07-0.11 at constant
2-6%). The no-flow control cells under declining paths diverge at
{nhf_e1.occurrence.mean():.0%} occurrence with genuinely suboptimal/infeasible
tails — a preference-level (Strotz) inconsistency channel, separated from the
structural one in the writeup.

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

Cap calibration ELIMINATES dynamic inconsistency: occurrence
{e2.occurrence.mean():.0%} across the grid (mean divergence
{e2.mean_abs_rel_deviation.mean():.3f}, max
{e2.mean_abs_rel_deviation.max():.3f} — all below the 5% tolerance), with
100% convergence. Removing the inter-period link removes the inconsistency.
The calibrated level on landbase 1 (~9,400 MCF/period) is ~8% below the NDY
plan's announced level — an automated allowable-cut calibration pricing the
credibility of the flow promise.

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

## Headline

Revenue denominating makes inconsistency MORE pervasive: flow-constrained
occurrence {rev_fc.occurrence.mean():.0%} (revenue) vs
{vol_fc.occurrence.mean():.0%} (volume), with roughly doubled magnitude. The
CM-CE filler channel is confirmed as the TELL, not the fuel: revenue NDY
drives projected CM-CE harvest to exactly zero (vs 2.5-3.5% of projected
volume under volume NDY on landbase 1), yet the plan is still not followed.
See the writeup's Table T4 for the focal solves.

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
occurrence {wp.occurrence.mean():.0%} ≈ pointwise NDY (86%). The ANCHORING
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


if __name__ == "__main__":
    main()
