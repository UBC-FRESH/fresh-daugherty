"""Tests for the Daugherty (1991) reconstruction framework (P1.1b framework)."""

from __future__ import annotations

import numpy as np
import pytest

from fresh_daugherty.instance.reconstruct import (
    RECONSTRUCTION_ASSUMPTIONS,
    EconomicsParams,
    YieldParams,
    best_rotation,
    escalated_price,
    faustmann_lev,
    yield_volume,
)
from fresh_daugherty.instance.thesis import THESIS_DISCOUNT_RATE

YP = YieldParams(vmax=30.0, k=0.03, m=3.0)
ECON = EconomicsParams(net_price_per_mcf=250.0, harvest_cost_per_mcf=100.0)


def test_yield_curve_shape() -> None:
    assert yield_volume(0.0, YP) == 0.0
    # Monotone increasing toward Vmax.
    v50, v100, v200 = (yield_volume(a, YP) for a in (50, 100, 200))
    assert 0 < v50 < v100 < v200 < YP.vmax


def test_faustmann_lev_perpetual_exceeds_single() -> None:
    # For a fixed rotation, the perpetual series (LEV) exceeds the
    # single-rotation PNV by the perpetual-rotation factor.
    single = faustmann_lev(90.0, yield_params=YP, econ=ECON, perpetual=False)
    perp = faustmann_lev(90.0, yield_params=YP, econ=ECON, perpetual=True)
    factor = 1.0 / (1.0 - np.exp(-THESIS_DISCOUNT_RATE * 90.0))
    assert perp == pytest.approx(single * factor)


def test_price_escalation() -> None:
    assert escalated_price(100.0, 0) == pytest.approx(100.0)
    # +1%/yr for 50 years, then flat.
    assert escalated_price(100.0, 50) == pytest.approx(100.0 * 1.01**50)
    assert escalated_price(100.0, 80) == pytest.approx(escalated_price(100.0, 50))


def test_lev_improves_with_price_escalation() -> None:
    flat = faustmann_lev(90.0, yield_params=YP, econ=ECON, price_escalation=False)
    esc = faustmann_lev(90.0, yield_params=YP, econ=ECON, price_escalation=True)
    assert esc > flat


def test_best_rotation_within_range() -> None:
    r, lev = best_rotation(YP, ECON, (60, 150))
    assert 60 <= r <= 150
    assert np.isfinite(lev)


def test_negative_economics_give_negative_lev() -> None:
    # A stand whose net price never covers harvest cost has a negative LEV
    # (the CM-CE negatively-valued case).
    bad = EconomicsParams(net_price_per_mcf=50.0, harvest_cost_per_mcf=100.0)
    _, lev = best_rotation(YP, bad, (110, 190))
    assert lev < 0


def test_reconstruction_assumptions_documented() -> None:
    assert RECONSTRUCTION_ASSUMPTIONS
    assert all(isinstance(a, str) and a for a in RECONSTRUCTION_ASSUMPTIONS)
