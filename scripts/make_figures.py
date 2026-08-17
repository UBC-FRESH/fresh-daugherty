"""Generate the paper's figures from the experiment stack (tracked, reproducible).

Figure 1: the declining non-declining yield on the all-mature landbase 1 — the
open-loop plan's projected (non-declining) harvest trajectory vs the realized
sequential-replanning trajectory, for the NDY harvest-flow policy.

Run:  python scripts/make_figures.py
"""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

OUT = Path(__file__).resolve().parent.parent / "paper" / "figures"


def fig_declining_ndy(out: Path) -> Path:
    """Open-loop projection vs realized replanned trajectory, landbase 1."""
    from fresh_daugherty.experiments import run_experiment
    from fresh_daugherty.instance.reconstruct import calibrate
    from fresh_daugherty.instance.thesis import HARVEST_FLOW_POLICIES

    calibrate()
    pol = {p.code: p for p in HARVEST_FLOW_POLICIES}
    r = run_experiment(
        landbase=1,
        discount_rate=0.04,
        flow_tolerance=0.0,
        horizon=15,
        workdir="/tmp/fig1",
        flow_policy=pol["NDY"],
    )
    periods = list(range(1, len(r.projected) + 1))
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(
        periods,
        [v / 1000 for v in r.projected],
        marker="o",
        ms=4,
        label="Open-loop plan (projected)",
        color="#1f4e79",
    )
    ax.plot(
        periods,
        [v / 1000 for v in r.realized],
        marker="s",
        ms=4,
        label="Sequential replanning (realized)",
        color="#c00000",
    )
    ax.set_xlabel("Planning period (10 years each)")
    ax.set_ylabel("Harvest volume (thousand MCF)")
    ax.set_title(
        "Landbase 1 (all mature), non-declining yield:\n"
        "the plan's level flow is not delivered under replanning"
    )
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "fig_declining_ndy.pdf")
    fig.savefig(out / "fig_declining_ndy.png", dpi=200)
    plt.close(fig)
    return out / "fig_declining_ndy.pdf"


if __name__ == "__main__":
    p = fig_declining_ndy(OUT)
    print(f"wrote {p}")
