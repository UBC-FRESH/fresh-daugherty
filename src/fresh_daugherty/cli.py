"""fresh-daugherty command-line interface (thin wrappers over the Python API)."""

from __future__ import annotations

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


@app.command("build-model")
def build_model() -> None:
    """Build the case-study harvest-scheduling model (Phase 1). Stub."""
    typer.echo("build-model: not implemented yet (Phase 1).")


@app.command("open-loop")
def open_loop() -> None:
    """Solve the open-loop harvest-scheduling LP (Phase 1). Stub."""
    typer.echo("open-loop: not implemented yet (Phase 1).")


@app.command("replan-run")
def replan_run() -> None:
    """Run the sequential-replanning simulator (Phase 3). Stub."""
    typer.echo("replan-run: not implemented yet (Phase 3).")


@app.command("consistency-run")
def consistency_run() -> None:
    """Run the consistent-solution (subgame-perfect) analysis (Phase 4). Stub."""
    typer.echo("consistency-run: not implemented yet (Phase 4).")


if __name__ == "__main__":
    app()
