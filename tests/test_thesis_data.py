"""Tests for the transcribed Daugherty (1991) thesis reference data (P1.1a)."""

from __future__ import annotations

from fresh_daugherty.instance import (
    HORIZON_YEARS,
    LANDBASE_ACRES,
    LANDBASES,
    MATURE_TYPE_PNV,
    N_PERIODS,
    PERIOD_LENGTH_YEARS,
    PNV_ROTATION_ANCHORS,
    ROTATION_RANGES,
    THESIS_DISCOUNT_RATE,
    Ecoclass,
    Prescription,
)


def test_horizon_and_discount() -> None:
    assert HORIZON_YEARS == 150
    assert N_PERIODS == 15
    assert PERIOD_LENGTH_YEARS == 10
    assert THESIS_DISCOUNT_RATE == 0.04


def test_four_ecoclasses_seven_prescriptions() -> None:
    assert len(Ecoclass) == 4
    assert len(Prescription) == 7


def test_rotation_ranges_cover_all_cells() -> None:
    # Every ecoclass x prescription cell is present (value or explicit None).
    assert len(ROTATION_RANGES) == 4 * 7
    for rng in ROTATION_RANGES.values():
        if rng is not None:
            assert rng.lo < rng.hi


def test_anchor_optimal_rotation_within_range() -> None:
    for key, anchor in PNV_ROTATION_ANCHORS.items():
        rng = ROTATION_RANGES[key]
        if anchor is None:
            assert rng is None
            continue
        assert rng is not None
        assert rng.lo <= anchor.optimal_rotation_yr <= rng.hi


def test_negatively_valued_strata_are_cm_ce() -> None:
    # The negatively-valued strata (Daugherty's inconsistency drivers) are all
    # in the CM-CE ecoclass.
    negative = [
        key for key, a in PNV_ROTATION_ANCHORS.items() if a is not None and a.max_pnv_per_ac < 0
    ]
    assert negative and all(key[0] is Ecoclass.CM_CE for key in negative)


def test_mature_type_anchors() -> None:
    assert len(MATURE_TYPE_PNV) == 5
    for mt in MATURE_TYPE_PNV:
        if mt.ecoclass is Ecoclass.CM_CE:
            # CM-CE sawtimber is negatively-valued, and its negative PNV
            # *decreases* (improves) over time (thesis p.72: "the exception").
            assert mt.pnv_period1_per_ac < 0 and mt.pnv_period2_per_ac < 0
            assert mt.pnv_period2_per_ac > mt.pnv_period1_per_ac
        else:
            # The other mature types are positively valued and decline
            # (financially over-mature) from period 1 to period 2.
            assert mt.pnv_period1_per_ac > 0 and mt.pnv_period2_per_ac > 0
            assert mt.pnv_period2_per_ac < mt.pnv_period1_per_ac


def test_eighteen_landbases() -> None:
    assert len(LANDBASES) == 18
    assert [lb.id for lb in LANDBASES] == list(range(1, 19))
    assert LANDBASE_ACRES == 10_000.0
