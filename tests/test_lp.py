"""Tests for the case-study ws3 model and open-loop LP (P1.2)."""

from __future__ import annotations

import pytest

from fresh_daugherty.instance.landbases import landbase_areas
from fresh_daugherty.lp import add_open_loop_problem, solve_open_loop
from fresh_daugherty.model import (
    bootstrap_model,
    build_woodstock_sections,
    prepare_optimization,
)


@pytest.fixture(scope="module")
def solved(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("model")
    areas = landbase_areas(1)
    build_woodstock_sections(tmp / "model", areas=areas)
    model = prepare_optimization(bootstrap_model(tmp / "model", horizon=15), horizon=15)
    problem = add_open_loop_problem(model)
    df = solve_open_loop(model, problem)
    return model, problem, df


def test_model_builds_with_five_themes(solved) -> None:
    model, _, _ = solved
    assert model.nthemes() == 5
    assert len(model.dtypes) > 0


def test_open_loop_solves_optimal(solved) -> None:
    _, problem, _ = solved
    assert problem.status() == "optimal"


def test_even_flow_holds(solved) -> None:
    """Harvest volume per period stays within the 5% even-flow band of period 1."""
    _, _, df = solved
    v = df["harvest_volume_mcf"].to_numpy()
    assert v[0] > 0
    for x in v[1:]:
        assert abs(x - v[0]) <= 0.05 * v[0] + 1e-6


def test_mature_timber_is_drawn_down(solved) -> None:
    """Growing stock declines as the over-mature timber is harvested."""
    _, _, df = solved
    gs = df["growing_stock_mcf"].to_numpy()
    assert gs[-1] < gs[0]


def test_landbase_area_conserved_initially() -> None:
    areas = landbase_areas(1)
    assert areas["area_ac"].sum() == pytest.approx(10_000.0)
    areas2 = landbase_areas(2)
    assert areas2["area_ac"].sum() == pytest.approx(10_000.0)
    # Landbase 2 excludes CM-CE.
    assert "CMCE" not in set(areas2["ecoclass"])
