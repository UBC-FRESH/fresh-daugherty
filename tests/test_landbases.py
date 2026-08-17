"""Tests for the 18 initial forest conditions (thesis Table 5.5)."""

from __future__ import annotations

import pytest

from fresh_daugherty.instance.landbases import landbase_areas


@pytest.mark.parametrize("landbase_id", list(range(1, 19)))
def test_all_landbases_build_and_conserve_area(landbase_id: int) -> None:
    """All 18 landbases build and cover 10,000 acres."""
    areas = landbase_areas(landbase_id)
    assert areas["area_ac"].sum() == pytest.approx(10_000.0)


def test_area_control_conversion_fraction() -> None:
    """Area-control derivation converts years/rotation of the base to regenerated.

    Landbase 3 = landbase 1 after 40 yrs at 100-yr rotation -> 40% regenerated.
    Landbase 7 = landbase 1 after 70 yrs at 70-yr rotation -> 100% regenerated.
    """
    lb3 = landbase_areas(3)
    regen3 = lb3[lb3["origin"] == "regenerated"]["area_ac"].sum()
    assert regen3 == pytest.approx(4_000.0)  # 40/100 of 10,000 ac
    lb7 = landbase_areas(7)
    regen7 = lb7[lb7["origin"] == "regenerated"]["area_ac"].sum()
    assert regen7 == pytest.approx(10_000.0)  # 70/70 -> fully converted


def test_area_control_regenerated_cohorts_age(self=None) -> None:
    """Derived landbases carry a gradient of regenerated cohort ages."""
    lb3 = landbase_areas(3)
    ages = sorted(lb3[lb3["origin"] == "regenerated"]["age"].unique())
    # 40 years of harvest at 10-yr periods -> cohorts at ages 10, 20, 30, 40.
    assert ages == [10, 20, 30, 40]
