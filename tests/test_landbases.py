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


def _eco_share(areas) -> dict[str, float]:
    return (areas.groupby("ecoclass")["area_ac"].sum() / areas["area_ac"].sum()).to_dict()


@pytest.mark.parametrize("landbase_id", list(range(9, 19)))
def test_young_growth_landbases_exclude_cmce(landbase_id: int) -> None:
    """P16.4 (#95): thesis p. 79 --- landbases 9-18 do not include the
    negatively valued CM-CE ecoclass (the earlier construction gave them
    13-18% CM-CE), and contain no mature types (p. 78)."""
    areas = landbase_areas(landbase_id)
    assert "CMCE" not in set(areas["ecoclass"])
    assert set(areas["origin"]) == {"regenerated"}


@pytest.mark.parametrize("landbase_id", [9, 10])
def test_structured_young_growth_composition(landbase_id: int) -> None:
    """Landbase 9 (p. 79): half CH-CW, the rest split CD-CP/CR-CF, the most
    intensive prescriptions split equally with/without commercial thinning;
    landbase 10 the same shares and prescriptions with irregular ages."""
    areas = landbase_areas(landbase_id)
    assert _eco_share(areas) == pytest.approx({"CHCW": 0.5, "CDCP": 0.25, "CRCF": 0.25})
    by = areas.groupby(["ecoclass", "rx"])["area_ac"].sum().to_dict()
    assert by == pytest.approx(
        {
            ("CHCW", "rx5"): 2500.0,
            ("CHCW", "rx7"): 2500.0,
            ("CDCP", "rx5"): 1250.0,
            ("CDCP", "rx7"): 1250.0,
            ("CRCF", "rx4"): 1250.0,
            ("CRCF", "rx6"): 1250.0,
        }
    )
    per_age = areas.groupby(["ecoclass", "rx", "age"])["area_ac"].sum()
    if landbase_id == 9:
        # equal acres in every age class within each (ecoclass, prescription) cell
        assert (per_age.groupby(level=[0, 1]).nunique() == 1).all()
    else:
        assert per_age.std() > 0.1 * per_age.mean()  # irregular


def test_area_control_history_follows_thesis() -> None:
    """Landbases 3-8 (p. 79): highest-volume mature stands harvested first;
    regeneration under prescriptions 1-2 (1 only on CR-CF); landbases 7-8 give
    the last 30 years' harvests early cultural treatments (prescription 4)."""
    lb3 = landbase_areas(3)
    regen = lb3[lb3["origin"] == "regenerated"]
    assert set(regen["rx"]) <= {"rx1", "rx2"}
    assert set(regen.loc[regen["rx"] == "rx1", "ecoclass"]) == {"CRCF"}
    # Highest volume first: CH-CW sawtimber (10.3 MCF/ac) then CR-CF (8.4) go first.
    remaining = lb3[lb3["origin"] == "existing"].groupby(["ecoclass", "rx"])["area_ac"].sum()
    assert ("CHCW", "mature") not in remaining.index
    assert ("CRCF", "mature") not in remaining.index
    assert remaining[("CMCE", "mature")] == pytest.approx(2000.0)
    lb7 = landbase_areas(7)
    young = lb7[lb7["age"] <= 30]
    assert set(young["rx"]) == {"rx4"}
    assert young["area_ac"].sum() == pytest.approx(3 * 10_000 / 7)
    assert set(lb7.loc[lb7["age"] > 30, "rx"]) <= {"rx1", "rx2"}


@pytest.mark.parametrize("landbase_id", list(range(11, 19)))
def test_random_landbases_cover_all_intensities(landbase_id: int) -> None:
    """Landbases 11-18 (p. 79): random, on average equal acres in all
    management intensities; every prescription and age class present."""
    areas = landbase_areas(landbase_id)
    assert set(areas["rx"]) == {f"rx{k}" for k in range(1, 8)}
    assert len(set(areas["age"])) == 12
