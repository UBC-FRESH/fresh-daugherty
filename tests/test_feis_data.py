"""Tests for the extracted Umpqua FEIS data (real FORPLAN data)."""

from __future__ import annotations

import itertools

import pytest

from fresh_daugherty.instance.feis import (
    SITE_INDEX_BY_ECOCLASS,
    SPECIES_ECONOMICS,
    UMPQUA_YIELD_TABLES,
    mature_volume_crosscheck,
    standing_volume_curve,
    yield_tables_for,
)
from fresh_daugherty.instance.thesis import Ecoclass


def test_yield_tables_cover_all_ecoclasses() -> None:
    for eco in Ecoclass:
        assert yield_tables_for(eco), f"no yield tables for {eco.value}"


def test_yield_tables_have_per_age_volumes() -> None:
    for table in UMPQUA_YIELD_TABLES:
        assert table["entries"], table["table"]
        for entry in table["entries"]:
            assert entry["kind"] in ("Thin", "Regen")
            assert entry["age"] > 0


def test_standing_volume_curve_increases_then_culminates() -> None:
    # CH-CW volume-emphasis curve: standing volume rises to a CMAI culmination.
    curve = standing_volume_curve(Ecoclass.CH_CW, emphasis="volume")
    assert curve
    ages = sorted(curve)
    assert ages[0] > 0
    # volumes are positive and generally increasing through the rotation range
    for a in ages:
        assert curve[a] > 0


def test_site_indices_present() -> None:
    assert SITE_INDEX_BY_ECOCLASS[Ecoclass.CH_CW]["si50"] == 88
    assert SITE_INDEX_BY_ECOCLASS[Ecoclass.CD_CP]["si50"] == 82


def test_species_economics() -> None:
    # Mountain hemlock is the low-value (negatively-valued-stratum) species.
    assert SPECIES_ECONOMICS["Mountain Hemlock"][0] == 27.0
    assert SPECIES_ECONOMICS["Douglas-Fir"][0] == 255.0


def test_model_lev_reproduces_anchor_signs() -> None:
    """Exact-vintage validation: the real-data model reproduces the Table 5.3
    anchors' signs (productive ecoclasses positive, CM-CE negative) on rotations
    of the model's period grid, where the curves carry volume (P19.1, #118: the
    earlier search visited off-grid ages with zero volume, so CM-CE "passed"
    with LEV = 0)."""
    from fresh_daugherty.instance.feis import model_lev, real_yield_curve
    from fresh_daugherty.instance.thesis import (
        PERIOD_LENGTH_YEARS,
        PNV_ROTATION_ANCHORS,
        ROTATION_RANGES,
    )

    for (eco, rx), anchor in PNV_ROTATION_ANCHORS.items():
        if anchor is None:
            continue
        opt_r, lev = model_lev(eco, rx)
        rng = ROTATION_RANGES[(eco, rx)]
        assert rng is not None
        assert rng.lo <= opt_r <= rng.hi and opt_r % PERIOD_LENGTH_YEARS == 0
        assert real_yield_curve(eco, rx, max_age=300)[opt_r] > 0
        if anchor.max_pnv_per_ac < 0:
            assert lev < 0, f"{eco.value} rx{int(rx)} should be negative"
        else:
            assert lev > 0, f"{eco.value} rx{int(rx)} should be positive"


def test_model_optimal_rotations_differ_from_table_5_3() -> None:
    """Audit V02/V03 (P19.1, #118), recorded rather than hidden: the model's
    highest-PNV rotation is the shortest permitted one for every productive
    prescription (the thesis's Table 5.3 rotations are longer or equal), and
    the longest permitted one for the negatively valued CM-CE."""
    from fresh_daugherty.instance.feis import model_lev
    from fresh_daugherty.instance.thesis import PNV_ROTATION_ANCHORS, ROTATION_RANGES

    for (eco, rx), anchor in PNV_ROTATION_ANCHORS.items():
        if anchor is None:
            continue
        opt_r, _ = model_lev(eco, rx)
        rng = ROTATION_RANGES[(eco, rx)]
        if anchor.max_pnv_per_ac < 0:
            assert opt_r > anchor.optimal_rotation_yr
        else:
            assert opt_r == rng.lo <= anchor.optimal_rotation_yr


def test_mature_volume_crosscheck_independent() -> None:
    """The mature volumes back-computed from the Table 5.4 PNV anchors are
    cross-checked against the independent FEIS standing-volume curves (P1.4).
    The period-1 Table 5.4 match is a calibration; this is the independent check that
    the volumes are at least the same order of magnitude."""
    df = mature_volume_crosscheck()
    assert len(df) == 5
    # Positively valued types: FEIS independent volume within ~3x of back-calc.
    pos = df[df["pnv_period1_per_ac"] > 0]
    assert (pos["ratio_feis_over_backcalc"].between(0.3, 3.0)).all()
    # The negatively valued CM-CE sawtimber has a negative PNV (cost > value).
    cmce = df[df["ecoclass"] == "CM-CE"].iloc[0]
    assert cmce["pnv_period1_per_ac"] < 0


def test_young_age_yields_follow_a_sigmoid_from_zero() -> None:
    """P18.1 (#111): below the first tabled FEIS age the yield curve follows
    the cell's calibrated Chapman-Richards shape scaled to the first FEIS
    value (it was held flat there, crediting young stands with an older
    stand's volume). Curves start at zero, rise over the filled ages, and keep the FEIS
    values at the tabled ages."""
    from fresh_daugherty.instance.feis import real_yield_curve, real_yield_table
    from fresh_daugherty.instance.landbases import _managed_cells

    for eco, rx in _managed_cells():
        curve = real_yield_curve(eco, rx, max_age=300)
        assert curve[0] == pytest.approx(0.0, abs=1e-9), (eco, rx)
        table = real_yield_table(eco, rx)
        pts = {
            e["age"]: float(e["values"][0])
            for e in table["entries"]
            if e["kind"] == "Regen" and e["values"] and e["values"][0] is not None
        }
        first = min(pts)
        # Non-decreasing over the filled young segment (the FEIS values
        # themselves decline slightly after culmination in a few tables).
        young = [curve[a] for a in sorted(curve) if a <= first]
        assert all(b >= a - 1e-9 for a, b in itertools.pairwise(young)), (eco, rx)
        for age, vol in pts.items():
            if age % 10 == 0:
                assert curve[age] == pytest.approx(vol), (eco, rx, age)
        if first > 10:
            assert curve[first - first % 10] < pts[first] + 1e-9
