"""Tests for the sequential-replanning simulator + inconsistency (P3)."""

from __future__ import annotations

import pytest

from fresh_daugherty.instance.landbases import landbase_areas
from fresh_daugherty.instance.reconstruct import calibrate
from fresh_daugherty.model import bootstrap_model, build_woodstock_sections, prepare_optimization
from fresh_daugherty.replan import (
    inconsistency_metrics,
    open_loop_projection,
    sequential_replan,
)


@pytest.fixture(scope="module")
def replan_result(tmp_path_factory):
    calibrate()  # warm the calibration cache once
    tmp = tmp_path_factory.mktemp("replan")
    areas = landbase_areas(1)
    build_woodstock_sections(tmp / "model", areas=areas)
    model = prepare_optimization(bootstrap_model(tmp / "model", horizon=6), horizon=6)
    projected = open_loop_projection(model)
    realized = sequential_replan(model, workdir=tmp / "replans")
    return projected, list(realized["harvest_volume_mcf"])


def test_open_loop_projection_is_even_flow(replan_result) -> None:
    projected, _ = replan_result
    assert projected[0] > 0
    for v in projected[1:]:
        assert abs(v - projected[0]) <= 0.05 * projected[0] + 1e-6


def test_period_one_is_consistent(replan_result) -> None:
    # The immediate (period-1) decision is always followed; inconsistency
    # appears in the tail.
    projected, realized = replan_result
    assert realized[0] == pytest.approx(projected[0], rel=1e-6)


def test_plan_tail_is_not_followed(replan_result) -> None:
    """Dynamic inconsistency: the open-loop plan's tail is not what the
    realized replanned trajectory delivers."""
    projected, realized = replan_result
    m = inconsistency_metrics(projected, realized)
    assert m["mean_abs_rel_deviation"] > 0.10


def test_replanning_is_reproducible(tmp_path) -> None:
    calibrate()

    def run():
        areas = landbase_areas(1)
        build_woodstock_sections(tmp_path / "m", areas=areas)
        model = prepare_optimization(bootstrap_model(tmp_path / "m", horizon=5), horizon=5)
        return list(sequential_replan(model, workdir=tmp_path / "r")["harvest_volume_mcf"])

    first, second = run(), run()
    assert first == second
