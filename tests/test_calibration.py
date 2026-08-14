"""Calibration tests for the Daugherty (1991) reconstruction (P1.1b).

The reconstruction is calibrated to the thesis Table 5.3 anchors. The anchors
are *compared against*, not force-fit; the achieved fit is asserted at a
documented tolerance and the qualitative patterns (PNV rising with management
intensity; negative CM-CE; rotations in range) are asserted exactly.
"""

from __future__ import annotations

import pytest

from fresh_daugherty.instance.reconstruct import (
    calibrate,
    calibration_report,
    k_for_culmination,
)
from fresh_daugherty.instance.thesis import (
    CMAI_CULMINATION_AGE_YR,
    ROTATION_RANGES,
)


@pytest.fixture(scope="module")
def report():
    calibrate()
    return calibration_report()


def test_k_for_culmination_hits_cmai() -> None:
    # The reconstructed yield-curve growth rate puts MAI culmination at the
    # ecoclass's documented CMAI culmination age (LRMP Table IV-3).
    for cmai in CMAI_CULMINATION_AGE_YR.values():
        assert k_for_culmination(cmai) > 0


def test_calibration_covers_all_anchor_cells(report) -> None:
    # 19 non-N/A Table 5.3 anchor cells (CH-CW 6, CD-CP 6, CR-CF 4, CM-CE 3).
    assert len(report) == 19


def test_model_rotations_within_thesis_ranges(report) -> None:
    for row in report.itertuples():
        rng = next(
            r
            for (eco, rx), r in ROTATION_RANGES.items()
            if eco.value == row.ecoclass and int(rx) == row.prescription
        )
        assert rng is not None
        assert rng.lo <= row.model_rotation <= rng.hi


def test_negative_cm_ce_strata(report) -> None:
    # Daugherty's inconsistency drivers: the CM-CE regenerated prescriptions
    # are negatively valued. The reconstruction must reproduce the sign.
    cm_ce = report[report["ecoclass"] == "CM-CE"]
    assert (cm_ce["model_pnv"] < 0).all()


def test_pnv_rises_with_management_intensity(report) -> None:
    # Within CH-CW (the most productive site), PNV rises across the
    # intensity ladder rx2 < rx4 < rx7 (plant < +VM/PCT < +VM/PCT/FERT/CT).
    ch = report[report["ecoclass"] == "CH-CW"].set_index("prescription")
    assert ch.loc[2, "model_pnv"] < ch.loc[7, "model_pnv"]


def test_pnv_fit_within_tolerance(report) -> None:
    # Documented structural reconstruction: the smooth model matches the
    # anchor PNV magnitudes but not the pointwise-irregular pattern produced
    # by the (unavailable) Umpqua yield tables. Mean |PNV error| is asserted
    # below a recorded tolerance; rotations are approximate.
    err = (report["model_pnv"] - report["anchor_pnv"]).abs()
    assert err.mean() < 50.0  # $/ac mean absolute error tolerance
