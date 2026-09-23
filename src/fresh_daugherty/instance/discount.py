"""Time-varying discount-rate paths (Phase 9 / E1, issue #53).

The core grid replicates the thesis's *constant* discount rate
(``DISCOUNT_RATES``: 0%, 2%, 4%, 6%; thesis p.80). E1 tests whether a
*declining* rate mitigates or eliminates dynamic inconsistency, using two
non-constant path families:

- ``linear``: the annual rate declines linearly from ``r0`` at period 1 by
  ``slope_per_period`` per period, floored at ``floor``;
- ``inverse-j``: the annual rate is constant at ``r0`` for the first
  ``hold_periods`` periods (~10--20 years), then decays exponentially at
  ``decay_lambda`` per period.

A path specifies the *annual* discount rate in effect during each (10-year)
period of a subproblem; the cumulative discount factor for period ``t`` is
the product form

    factor_t = prod_{s=1..t} (1 + r_s)^(-period_length),

which for a constant path ``r_s = r`` reproduces the existing scalar
convention ``(1 + r)^(-t * period_length)`` exactly (bit-identical wiring is
verified by the tests here and by the P9.2 LP-builder regression).

Paths are indexed by the *relative* period of each replanning subproblem
(each replanning planner applies the path from her own present, matching the
existing convention that discounting stays relative to the subproblem's
present while price escalation is calendar-absolute; see ``lp.py``). The
calendar-absolute reading is a possible sensitivity analysis, not the
default.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from fresh_daugherty.instance.thesis import N_PERIODS, PERIOD_LENGTH_YEARS


class DiscountPathFamily(StrEnum):
    """The discount-rate path families (E1)."""

    CONSTANT = "constant"  # the thesis's flat rate (control)
    LINEAR = "linear"  # linearly declining to a floor
    INVERSE_J = "inverse-j"  # constant for k periods, then exponential decay


@dataclass(frozen=True)
class DiscountPath:
    """A per-period discount-rate path for the open-loop LP objective.

    ``code`` is a filesystem-safe slug used in grid cell workdirs and records.
    ``note`` is the provenance record (why this parameterization). Family-
    specific fields: ``slope_per_period``/``floor`` (linear),
    ``hold_periods``/``decay_lambda`` (inverse-j).
    """

    code: str
    family: DiscountPathFamily
    r0: float
    slope_per_period: float = 0.0
    floor: float = 0.0
    hold_periods: int = 0
    decay_lambda: float = 0.0
    note: str = ""

    def __post_init__(self) -> None:
        if not self.r0 >= 0.0:
            raise ValueError(f"r0 must be non-negative, got {self.r0}")
        if self.family is DiscountPathFamily.LINEAR:
            if not self.slope_per_period > 0.0:
                raise ValueError("linear paths require slope_per_period > 0")
            if not (0.0 <= self.floor <= self.r0):
                raise ValueError("linear paths require 0 <= floor <= r0")
        if self.family is DiscountPathFamily.INVERSE_J:
            if self.hold_periods < 1:
                raise ValueError("inverse-j paths require hold_periods >= 1")
            if not self.decay_lambda > 0.0:
                raise ValueError("inverse-j paths require decay_lambda > 0")

    def rate(self, period: int) -> float:
        """The annual discount rate in effect during ``period`` (1-based)."""
        if period < 1:
            raise ValueError(f"period is 1-based, got {period}")
        if self.family is DiscountPathFamily.LINEAR:
            return max(self.r0 - self.slope_per_period * (period - 1), self.floor)
        if self.family is DiscountPathFamily.INVERSE_J and period > self.hold_periods:
            return self.r0 * math.exp(-self.decay_lambda * (period - self.hold_periods))
        return self.r0  # constant, or the inverse-j hold segment

    def factors(
        self, horizon: int = N_PERIODS, period_length: int = PERIOD_LENGTH_YEARS
    ) -> tuple[float, ...]:
        """Cumulative per-period discount factors ``factor_1..factor_horizon``.

        ``factor_t = prod_{s<=t} (1 + rate(s))^(-period_length)``. Constant
        paths compute ``(1 + r0)^(-t * period_length)`` directly per period so
        the E1 control is bit-identical to the existing scalar LP convention
        (cumulative multiplication would differ in the last float bits).
        """
        if self.family is DiscountPathFamily.CONSTANT:
            return tuple((1.0 + self.r0) ** (-t * period_length) for t in range(1, horizon + 1))
        out: list[float] = []
        cumulative = 1.0
        for t in range(1, horizon + 1):
            cumulative *= (1.0 + self.rate(t)) ** (-period_length)
            out.append(cumulative)
        return tuple(out)


def constant_path(rate: float) -> DiscountPath:
    """A constant path for one of the thesis's flat rates (the E1 control)."""
    return DiscountPath(
        code=f"const-{rate:.0%}".replace("%", "pc"),
        family=DiscountPathFamily.CONSTANT,
        r0=rate,
        note=f"Thesis constant rate {rate:.0%} (p.80); the E1 control.",
    )


#: The fixed E1 parameter set (P9.1): 2 linear + 2 inverse-j paths, evaluated
#: against the constant-rate control (the core grid's four flat rates). Rates
#: are annual; periods are 10 years.
DISCOUNT_PATHS: tuple[DiscountPath, ...] = (
    DiscountPath(
        code="linear-4pc-0pc",
        family=DiscountPathFamily.LINEAR,
        r0=0.04,
        slope_per_period=0.04 / (N_PERIODS - 1),
        floor=0.0,
        note="Linear decline from the thesis's 4% base rate at period 1 to 0% at "
        "the final period (0% beyond).",
    ),
    DiscountPath(
        code="linear-6pc-0pc",
        family=DiscountPathFamily.LINEAR,
        r0=0.06,
        slope_per_period=0.06 / (N_PERIODS - 1),
        floor=0.0,
        note="Linear decline from the thesis's 6% high rate at period 1 to 0% at "
        "the final period (0% beyond).",
    ),
    DiscountPath(
        code="invj-4pc-k1",
        family=DiscountPathFamily.INVERSE_J,
        r0=0.04,
        hold_periods=1,
        decay_lambda=math.log(2.0),
        note="Constant at the thesis's 4% base rate for the first period (~10 "
        "years), then exponential decay halving the rate each period.",
    ),
    DiscountPath(
        code="invj-4pc-k2",
        family=DiscountPathFamily.INVERSE_J,
        r0=0.04,
        hold_periods=2,
        decay_lambda=math.log(2.0),
        note="Constant at the thesis's 4% base rate for the first two periods "
        "(~20 years), then exponential decay halving the rate each period.",
    ),
)

_DISCOUNT_PATHS_BY_CODE = {p.code: p for p in DISCOUNT_PATHS}


def discount_path(code: str) -> DiscountPath:
    """Look up a registered E1 discount path by its slug."""
    try:
        return _DISCOUNT_PATHS_BY_CODE[code]
    except KeyError:
        raise KeyError(
            f"unknown discount path {code!r}; registered: {sorted(_DISCOUNT_PATHS_BY_CODE)}"
        ) from None


__all__ = [
    "DISCOUNT_PATHS",
    "DiscountPath",
    "DiscountPathFamily",
    "constant_path",
    "discount_path",
]
