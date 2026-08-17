"""fresh-daugherty command-line interface (thin wrappers over the Python API)."""

from __future__ import annotations

from pathlib import Path

import typer

from fresh_daugherty import __version__

app = typer.Typer(
    name="fresh-daugherty",
    help=(
        "Open, reproducible ws3-based reproduction of Daugherty (1991): "
        "dynamic inconsistency in LP-based forest planning models."
    ),
    add_completion=False,
)


@app.command("version")
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


@app.command("open-loop")
def open_loop(
    landbase: int = typer.Option(1, "--landbase", help="Landbase id (1-18)."),
    horizon: int = typer.Option(15, "--horizon", min=1),
    discount_rate: float = typer.Option(0.04, "--discount-rate"),
    flow_tolerance: float = typer.Option(0.05, "--flow-tolerance"),
    out_dir: Path = typer.Option(Path("outputs") / "open_loop", "--out-dir"),
) -> None:
    """Solve the open-loop harvest-scheduling LP (Model I) on a landbase."""
    from fresh_daugherty.instance.landbases import landbase_areas
    from fresh_daugherty.lp import add_open_loop_problem, solve_open_loop
    from fresh_daugherty.model import (
        bootstrap_model,
        build_woodstock_sections,
        prepare_optimization,
    )

    areas = landbase_areas(landbase)
    build_woodstock_sections(out_dir / "model", areas=areas)
    model = prepare_optimization(
        bootstrap_model(out_dir / "model", horizon=horizon), horizon=horizon
    )
    problem = add_open_loop_problem(
        model, flow_coefficient=flow_tolerance, discount_rate=discount_rate
    )
    results = solve_open_loop(model, problem)
    typer.echo(f"open-loop (landbase {landbase}, horizon {horizon}, rate {discount_rate}):")
    typer.echo(f"  status: {problem.status()}")
    typer.echo(f"  period-1 harvest volume: {results['harvest_volume_mcf'].iloc[0]:,.0f} MCF")
    typer.echo(f"  total harvest volume: {results['harvest_volume_mcf'].sum():,.0f} MCF")
    out_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(out_dir / "open_loop.csv", index=False)
    typer.echo(f"  wrote {out_dir / 'open_loop.csv'}")


@app.command("replan-run")
def replan_run(
    landbase: int = typer.Option(1, "--landbase", help="Landbase id (1-18)."),
    horizon: int = typer.Option(15, "--horizon", min=1),
    discount_rate: float = typer.Option(0.04, "--discount-rate"),
    flow_tolerance: float = typer.Option(0.05, "--flow-tolerance"),
    out_dir: Path = typer.Option(Path("outputs") / "replan", "--out-dir"),
) -> None:
    """Run the sequential-replanning simulator and report the inconsistency."""
    from fresh_daugherty.instance.landbases import landbase_areas
    from fresh_daugherty.model import (
        bootstrap_model,
        build_woodstock_sections,
        prepare_optimization,
    )
    from fresh_daugherty.replan import (
        inconsistency_metrics,
        open_loop_projection,
        sequential_replan,
    )

    areas = landbase_areas(landbase)
    build_woodstock_sections(out_dir / "model", areas=areas)
    model = prepare_optimization(
        bootstrap_model(out_dir / "model", horizon=horizon), horizon=horizon
    )
    projected = open_loop_projection(
        model, discount_rate=discount_rate, flow_tolerance=flow_tolerance
    )
    realized = sequential_replan(
        model,
        workdir=out_dir / "replans",
        discount_rate=discount_rate,
        flow_tolerance=flow_tolerance,
    )
    metrics = inconsistency_metrics(projected, list(realized["harvest_volume_mcf"]))
    typer.echo(f"sequential replan (landbase {landbase}, horizon {horizon}, rate {discount_rate}):")
    typer.echo(f"  projected period-1 volume: {projected[0]:,.0f} MCF")
    typer.echo(f"  mean |relative deviation|: {metrics['mean_abs_rel_deviation']:.1%}")
    typer.echo(f"  total realized vs projected: {metrics['total_rel_change']:+.1%}")
    typer.echo("  -> the open-loop plan is not followed (dynamic inconsistency)")


@app.command("grid")
def grid(
    landbases: str = typer.Option("1,2,9,10", "--landbases", help="Comma-separated landbase ids."),
    discount_rates: str = typer.Option(
        "0.0,0.02,0.04,0.06", "--discount-rates", help="Comma-separated rates."
    ),
    policies: str = typer.Option(
        "NHF,NDY,-10%,-20%,+/-10%,+/-20%",
        "--policies",
        help="Comma-separated Table 5.6 policy codes.",
    ),
    horizon: int = typer.Option(15, "--horizon", min=1),
    workers: int = typer.Option(
        1, "--workers", min=1, help="Parallel processes (grid is embarrassingly parallel)."
    ),
    out: Path = typer.Option(Path("results") / "experiments" / "grid.csv", "--out"),
) -> None:
    """Run the thesis experiment grid (landbase x discount rate x harvest-flow policy).

    Reproduces Daugherty (1991)'s experiment design: the Table 5.6 harvest-flow
    policies (consecutive sequential flow) crossed with discount rates and
    landbases. Writes the per-cell summary (occurrence + magnitude metrics) to
    ``--out`` and the full per-cell projected/realized harvest trajectories to
    ``<out-stem>_trajectories.csv``, in the tracked ``results/`` tree, so the
    complete benchmark record is public and reproducible.
    """
    from fresh_daugherty.experiments import run_policy_grid
    from fresh_daugherty.instance.reconstruct import calibrate
    from fresh_daugherty.instance.thesis import HARVEST_FLOW_POLICIES

    calibrate()
    lbs = tuple(int(x) for x in landbases.split(","))
    rates = tuple(float(x) for x in discount_rates.split(","))
    pol_by_code = {p.code: p for p in HARVEST_FLOW_POLICIES}
    pols = tuple(pol_by_code[c] for c in policies.split(","))
    summary, trajectories = run_policy_grid(
        landbases=lbs,
        discount_rates=rates,
        policies=pols,
        horizon=horizon,
        workdir=out.parent / "grid_work",
        workers=workers,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out, index=False)
    traj_out = out.with_name(out.stem + "_trajectories.csv")
    trajectories.to_csv(traj_out, index=False)
    typer.echo(f"wrote {traj_out} ({len(trajectories)} trajectory rows)")
    typer.echo(f"wrote {out} ({len(summary)} cells)")
    typer.echo(f"  occurrence rate: {summary['occurrence'].mean():.0%} of cells")


@app.command("consistency-run")
def consistency_run() -> None:
    """Run the consistent-solution (subgame-perfect) analysis (post-v0.1.0a1)."""
    typer.echo(
        "consistency-run: the consistent-solution construct is documented in "
        "planning/v0.1.0a1-plan.md and is post-v0.1.0a1 (see ROADMAP)."
    )


if __name__ == "__main__":
    app()
