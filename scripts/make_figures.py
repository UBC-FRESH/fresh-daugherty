"""Generate the manuscript's figures from the tracked experiment records.

Reads only ``results/experiments/*.csv`` (no solves) and writes the figures to
``results/analysis/manuscript_figures/`` with one shared style (font sizes,
width, colours; no in-figure titles, the captions carry the description):

- ``fig_declining_ndy``: landbase 1, NDY, 4% --- open-loop projection vs the
  realized sequential-replanning trajectory (core grid).
- ``fig_e1_magnitude``: E1 --- the magnitude of every flow-constrained scenario
  by discount scheme (constant rates vs declining paths), with the 5% occurrence
  tolerance and each scheme's occurrence share.
- ``fig_e2_ndy_vs_cap``: E2 --- landbase 1 at 4%, the NDY plan and its realized
  trajectory vs the calibrated max-harvest cap.

Run:  PYTHONPATH=src python scripts/make_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results" / "experiments"
OUT = ROOT / "results" / "analysis" / "manuscript_figures"

#: Shared style. Width matches a single-column text block (6.3 in).
WIDTH_IN = 6.3
STYLE = {
    "font.size": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "savefig.dpi": 300,
}
PLAN = "#1f4e79"  # announced / open-loop
REAL = "#c00000"  # realized under replanning
CAP = "#e07b00"  # E2 cap
GREY = "#9e9e9e"
DARK = "#404040"
VOLUME_LABEL = "Harvest (thousand MCF per period)"
TOLERANCE = 0.05


def _save(fig: plt.Figure, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf", metadata={"CreationDate": None})
    fig.savefig(OUT / f"{name}.png")
    plt.close(fig)
    return OUT / f"{name}.pdf"


def _cell(traj: pd.DataFrame, **keys) -> pd.DataFrame:
    mask = np.ones(len(traj), dtype=bool)
    for k, v in keys.items():
        mask &= traj[k] == v
    return traj[mask].sort_values("period")


def fig_declining_ndy() -> Path:
    t = _cell(
        pd.read_csv(RESULTS / "grid_trajectories.csv"),
        landbase=1,
        discount_rate=0.04,
        flow_policy="NDY",
    )
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 3.0))
    ax.plot(
        t.period,
        t.projected_mcf / 1000,
        marker="o",
        ms=3.5,
        color=PLAN,
        label="Open-loop plan (announced)",
    )
    ax.plot(
        t.period,
        t.realized_mcf / 1000,
        marker="s",
        ms=3.5,
        color=REAL,
        label="Sequential replanning (realized)",
    )
    ax.set_xlabel("Planning period (10 years)")
    ax.set_ylabel(VOLUME_LABEL)
    ax.set_xticks(range(1, int(t.period.max()) + 1))
    ax.legend(frameon=False)
    fig.tight_layout()
    return _save(fig, "fig_declining_ndy")


def fig_e1_magnitude() -> Path:
    core = pd.read_csv(RESULTS / "grid.csv")
    e1 = pd.read_csv(RESULTS / "grid_discount_paths.csv")
    core = core[core.flow_policy != "NHF"]
    e1 = e1[e1.flow_policy != "NHF"]
    schemes: list[tuple[str, pd.Series, str]] = [
        (f"constant\n{r:.0%}", core.loc[core.discount_rate == r, "mean_abs_rel_deviation"], GREY)
        for r in sorted(core.discount_rate.unique())
    ]
    labels = {
        "linear-4pc-0pc": "linear\n4%\u21920%",
        "linear-6pc-0pc": "linear\n6%\u21920%",
        "invj-4pc-k1": "inverse-j\n4%, k=1",
        "invj-4pc-k2": "inverse-j\n4%, k=2",
    }
    for code, lab in labels.items():
        schemes.append((lab, e1.loc[e1.discount_path == code, "mean_abs_rel_deviation"], DARK))
    rng = np.random.default_rng(0)
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 3.2))
    for i, (_lab, vals, colour) in enumerate(schemes):
        x = i + rng.uniform(-0.18, 0.18, size=len(vals))
        ax.scatter(x, vals, s=6, color=colour, alpha=0.6, linewidths=0)
        ax.plot([i - 0.28, i + 0.28], [vals.mean()] * 2, color="black", lw=1.2)
        ax.annotate(
            f"{(vals > TOLERANCE).mean():.0%}",
            (i, 1.0),
            xycoords=("data", "axes fraction"),
            ha="center",
            va="bottom",
            fontsize=7,
        )
    ax.axhline(TOLERANCE, color="black", lw=0.8, ls="--")
    ax.set_xticks(range(len(schemes)), [s[0] for s in schemes])
    ax.set_ylabel("Magnitude (mean divergence)")
    ax.set_xlim(-0.6, len(schemes) - 0.4)
    fig.tight_layout()
    return _save(fig, "fig_e1_magnitude")


def fig_e2_ndy_vs_cap() -> Path:
    ndy = _cell(
        pd.read_csv(RESULTS / "grid_trajectories.csv"),
        landbase=1,
        discount_rate=0.04,
        flow_policy="NDY",
    )
    cap = _cell(
        pd.read_csv(RESULTS / "grid_cap_search_trajectories.csv"), landbase=1, discount_rate=0.04
    )
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 3.0))
    ax.plot(ndy.period, ndy.projected_mcf / 1000, ls="--", color=PLAN, label="NDY plan (announced)")
    ax.plot(
        ndy.period,
        ndy.realized_mcf / 1000,
        color=REAL,
        marker="s",
        ms=3,
        label="NDY under replanning (realized)",
    )
    ax.plot(
        cap.period,
        cap.realized_mcf / 1000,
        color=CAP,
        marker="o",
        ms=3,
        label="Calibrated cap under replanning (realized)",
    )
    ax.set_xlabel("Planning period (10 years)")
    ax.set_ylabel(VOLUME_LABEL)
    ax.set_xticks(range(1, int(ndy.period.max()) + 1))
    ax.legend(frameon=False)
    fig.tight_layout()
    return _save(fig, "fig_e2_ndy_vs_cap")


def main() -> None:
    plt.rcParams.update(STYLE)
    for make in (fig_declining_ndy, fig_e1_magnitude, fig_e2_ndy_vs_cap):
        print(f"wrote {make()}")


if __name__ == "__main__":
    main()
