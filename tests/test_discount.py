"""Tests for the E1 time-varying discount-rate paths (P9.1, issue #53)."""

from __future__ import annotations

import itertools
import math

import pytest

from fresh_daugherty.instance.discount import (
    DISCOUNT_PATHS,
    DiscountPath,
    DiscountPathFamily,
    constant_path,
    discount_path,
)
from fresh_daugherty.instance.thesis import N_PERIODS, PERIOD_LENGTH_YEARS


def test_constant_factors_match_scalar_convention() -> None:
    # The constant path must reproduce the existing scalar LP convention
    # (1 + r)^(-t * period_length) exactly, for all four thesis rates.
    for rate in (0.0, 0.02, 0.04, 0.06):
        path = constant_path(rate)
        factors = path.factors()
        assert len(factors) == N_PERIODS
        for t, f in enumerate(factors, start=1):
            assert f == (1.0 + rate) ** (-t * PERIOD_LENGTH_YEARS)


def test_zero_rate_path_is_flat() -> None:
    assert constant_path(0.0).factors() == (1.0,) * N_PERIODS


def test_registry_codes_unique_and_lookup() -> None:
    codes = [p.code for p in DISCOUNT_PATHS]
    assert len(codes) == len(set(codes))
    for path in DISCOUNT_PATHS:
        assert discount_path(path.code) is path
    with pytest.raises(KeyError):
        discount_path("no-such-path")


def test_linear_path_shape() -> None:
    path = discount_path("linear-4pc-0pc")
    rates = [path.rate(t) for t in range(1, N_PERIODS + 1)]
    assert rates[0] == pytest.approx(0.04)
    # Monotone non-increasing, hitting the floor exactly at the final period.
    assert all(b <= a + 1e-15 for a, b in itertools.pairwise(rates))
    assert rates[-1] == pytest.approx(0.0)
    # Never below the floor, even far past the horizon.
    assert path.rate(N_PERIODS + 5) == 0.0


def test_inverse_j_path_shape() -> None:
    lam = math.log(2.0)
    for code, k in (("invj-4pc-k1", 1), ("invj-4pc-k2", 2)):
        path = discount_path(code)
        rates = [path.rate(t) for t in range(1, N_PERIODS + 1)]
        # Constant hold segment.
        assert rates[:k] == [0.04] * k
        # Strictly decreasing decay segment, halving per period.
        tail = rates[k:]
        assert all(b < a for a, b in itertools.pairwise(tail))
        assert tail[0] == pytest.approx(0.04 * math.exp(-lam))
        assert tail[1] / tail[0] == pytest.approx(math.exp(-lam))


def test_factors_properties() -> None:
    for path in DISCOUNT_PATHS:
        factors = path.factors()
        # First factor is the period-1 rate compounded over one period.
        assert factors[0] == (1.0 + path.rate(1)) ** (-PERIOD_LENGTH_YEARS)
        # Strictly positive, bounded by 1, non-increasing.
        assert all(0.0 < f <= 1.0 for f in factors)
        assert all(b <= a for a, b in itertools.pairwise(factors))
        # Product form: each factor is the previous times the per-period factor.
        for t in range(2, N_PERIODS + 1):
            per_period = (1.0 + path.rate(t)) ** (-PERIOD_LENGTH_YEARS)
            assert factors[t - 1] == factors[t - 2] * per_period


def test_declining_paths_discount_less_than_constant_in_tail() -> None:
    # The E1 premise: a declining rate weights the far future more heavily
    # than the constant 4% control, so tail factors exceed the control's.
    control = constant_path(0.04).factors()
    for code in ("linear-4pc-0pc", "invj-4pc-k1", "invj-4pc-k2"):
        factors = discount_path(code).factors()
        assert factors[-1] > control[-1]


def test_validation() -> None:
    with pytest.raises(ValueError, match="r0"):
        DiscountPath(code="bad", family=DiscountPathFamily.CONSTANT, r0=-0.01)
    with pytest.raises(ValueError, match="slope"):
        DiscountPath(code="bad", family=DiscountPathFamily.LINEAR, r0=0.04)
    with pytest.raises(ValueError, match="floor"):
        DiscountPath(
            code="bad",
            family=DiscountPathFamily.LINEAR,
            r0=0.04,
            slope_per_period=0.01,
            floor=0.05,
        )
    with pytest.raises(ValueError, match="hold_periods"):
        DiscountPath(code="bad", family=DiscountPathFamily.INVERSE_J, r0=0.04, decay_lambda=0.5)
    with pytest.raises(ValueError, match="decay_lambda"):
        DiscountPath(code="bad", family=DiscountPathFamily.INVERSE_J, r0=0.04, hold_periods=1)
    with pytest.raises(ValueError, match="1-based"):
        constant_path(0.04).rate(0)
