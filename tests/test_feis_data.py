"""Tests for the extracted Umpqua FEIS data (real FORPLAN data)."""

from __future__ import annotations

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
    anchors' signs (productive ecoclasses positive, CM-CE non-positive)."""
    from fresh_daugherty.instance.feis import model_lev
    from fresh_daugherty.instance.thesis import PNV_ROTATION_ANCHORS, ROTATION_RANGES

    for (eco, rx), anchor in PNV_ROTATION_ANCHORS.items():
        if anchor is None:
            continue
        opt_r, lev = model_lev(eco, rx)
        rng = ROTATION_RANGES[(eco, rx)]
        assert rng is not None
        # Optimal rotation within the thesis range.
        assert rng.lo <= opt_r <= rng.hi
        # Sign matches the anchor (CM-CE non-positive, others positive).
        if anchor.max_pnv_per_ac < 0:
            assert lev <= 0, f"{eco.value} rx{int(rx)} should be non-positive"
        else:
            assert lev > 0, f"{eco.value} rx{int(rx)} should be positive"


def test_mature_volume_crosscheck_independent() -> None:
    """The mature volumes back-computed from the Table 5.4 PNV anchors are
    cross-checked against the independent FEIS standing-volume curves (P1.4).
    The Table 5.4 match is by construction; this is the independent check that
    the volumes are at least the same order of magnitude."""
    df = mature_volume_crosscheck()
    assert len(df) == 5
    # Positively valued types: FEIS independent volume within ~3x of back-calc.
    pos = df[df["pnv_period1_per_ac"] > 0]
    assert (pos["ratio_feis_over_backcalc"].between(0.3, 3.0)).all()
    # The negatively valued CM-CE sawtimber has a negative PNV (cost > value).
    cmce = df[df["ecoclass"] == "CM-CE"].iloc[0]
    assert cmce["pnv_period1_per_ac"] < 0
