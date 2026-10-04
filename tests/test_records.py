"""Invariants over the tracked experiment records (P14.2, issue #77).

These tests read the committed CSVs under ``results/experiments/`` (no solves),
so stale or corrupted records fail CI even when the code that produced them
has since changed. The E3 defect fixed in P14 (#75) would have been caught
here: the realized period-1 harvest *is* the open-loop period-1 decision, so
period-1 announced must equal period-1 realized in every cell of every grid.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RECORDS = Path(__file__).resolve().parents[1] / "results" / "experiments"

_STALE_E3 = pytest.mark.xfail(
    strict=True,
    reason="E3 records predate the e72ab2b fix (announced = volume plan); re-run in #79",
)
_E2_OPEN = pytest.mark.xfail(
    strict=True,
    reason="E2 records predate the P14.3 fix (#78: projections at the 4% default); re-run in #79",
)


@pytest.mark.parametrize(
    "name",
    [
        "grid_trajectories.csv",
        "grid_discount_paths_trajectories.csv",
        "grid_rolling_mean_trajectories.csv",
        pytest.param("grid_cap_search_trajectories.csv", marks=_E2_OPEN),
        pytest.param("grid_value_flow_trajectories.csv", marks=_STALE_E3),
    ],
)
def test_period1_announced_equals_realized(name: str) -> None:
    df = pd.read_csv(RECORDS / name)
    first = df[df["period"] == 1]
    assert len(first) > 0
    bad = first[~np.isclose(first["projected_mcf"], first["realized_mcf"], rtol=1e-6, atol=1e-6)]
    assert bad.empty, f"{len(bad)}/{len(first)} cells violate the period-1 invariant:\n{bad.head()}"
