"""The cancellation ladder (§2.1). Pure rules.

Confirmed by the client 2026-09-13: measured in days' notice before departure
against the total trip cost, not the deposit alone. Figures here are the
pricing config's own defaults (deposit 30%, tiers at 90/60/30 days and
50/75/100%), invented for the test the same way every other worked example in
this suite is.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.modules.bookings.cancellation import (
    TIER_DEPOSIT_ONLY,
    TIER_FORFEIT,
    TIER_PEAK,
    TIER_SECOND,
    TIER_THIRD,
    Cancellation,
    PeakPeriod,
    check_cancellation,
    notice_days,
    peak_period_covering,
    settle_cancellation,
)

D = Decimal
DEPARTURE = date(2026, 12, 1)


def _check(*, on: date, pax: int = 2, exclusive: bool = False, peaks=None, total="200000"):
    return check_cancellation(
        total_amount=D(total),
        departure_date=DEPARTURE,
        notice_on=on,
        pax_count=pax,
        is_exclusive_use=exclusive,
        deposit_pct=D("30"),
        tier1_days=90,
        tier2_days=60,
        tier2_pct=D("50"),
        tier3_days=30,
        tier3_pct=D("75"),
        forfeit_pct=D("100"),
        group_pax_threshold=8,
        group_notice_extension_days=30,
        peak_periods=peaks,
    )


# --------------------------------------------------------------------------- #
# The standard ladder
# --------------------------------------------------------------------------- #


def test_ninety_days_or_more_retains_the_deposit_only():
    found = _check(on=date(2026, 9, 1))  # 91 days out
    assert found.notice_days == 91
    assert found.band == TIER_DEPOSIT_ONLY
    assert found.retained_pct == D("30")
    assert found.retained_amount == D("60000.00")


def test_sixty_to_eighty_nine_days_retains_half():
    found = _check(on=date(2026, 10, 1))  # 61 days out
    assert found.band == TIER_SECOND
    assert found.retained_pct == D("50")
    assert found.retained_amount == D("100000.00")


def test_thirty_to_fifty_nine_days_retains_three_quarters():
    found = _check(on=date(2026, 10, 20))  # 42 days out
    assert found.band == TIER_THIRD
    assert found.retained_pct == D("75")
    assert found.retained_amount == D("150000.00")


def test_under_thirty_days_retains_everything():
    found = _check(on=date(2026, 11, 15))  # 16 days out
    assert found.band == TIER_FORFEIT
    assert found.retained_pct == D("100")
    assert found.retained_amount == D("200000.00")


def test_a_no_show_is_the_forfeit_band_with_no_special_case():
    """A departure date already in the past gives a negative day-count, and
    that falls further below every threshold than a late cancellation does —
    nothing here checks for "did they actually show up" separately."""
    found = _check(on=date(2026, 12, 10))  # 9 days *after* departure
    assert found.notice_days == -9
    assert found.band == TIER_FORFEIT


def test_exactly_on_a_threshold_counts_for_that_threshold():
    """90 days is inside the 90+ band, not one day short of it."""
    found = _check(on=date(2026, 9, 2))  # exactly 90 days out
    assert found.notice_days == 90
    assert found.band == TIER_DEPOSIT_ONLY


# --------------------------------------------------------------------------- #
# Groups and exclusive-use
# --------------------------------------------------------------------------- #


def test_a_group_of_eight_or_more_gets_every_threshold_pushed_back():
    """61 days out is the standard ladder's second tier; for eight or more
    guests the same notice lands in the third tier instead (91 needed for the
    top band, 61 needed for the second, both now +30)."""
    standard = _check(on=date(2026, 10, 1), pax=7)
    group = _check(on=date(2026, 10, 1), pax=8)
    assert standard.band == TIER_SECOND
    assert group.band == TIER_THIRD
    assert group.is_group is True
    assert standard.is_group is False


def test_an_exclusive_use_booking_is_a_group_regardless_of_headcount():
    """A private two-person villa buyout is still a whole property held for
    one party — the extension applies by exclusivity, not only by size."""
    found = _check(on=date(2026, 10, 1), pax=2, exclusive=True)
    assert found.is_group is True
    assert found.band == TIER_THIRD


# --------------------------------------------------------------------------- #
# Peak periods
# --------------------------------------------------------------------------- #


def test_a_peak_period_forfeits_everything_regardless_of_notice():
    """91 days out would be deposit-only on the standard ladder; inside a
    configured peak period it is 100%, because the property's own terms are
    non-refundable from the moment of booking."""
    peaks = [PeakPeriod(start=date(2026, 11, 20), end=date(2026, 12, 10), label="Festive")]
    found = _check(on=date(2026, 9, 1), peaks=peaks)  # 91 days out
    assert found.is_peak is True
    assert found.band == TIER_PEAK
    assert found.retained_pct == D("100")
    assert found.peak_label == "Festive"


def test_a_departure_outside_every_configured_peak_period_uses_the_ladder():
    peaks = [PeakPeriod(start=date(2026, 3, 1), end=date(2026, 3, 20), label="Easter")]
    found = _check(on=date(2026, 9, 1), peaks=peaks)
    assert found.is_peak is False
    assert found.band == TIER_DEPOSIT_ONLY


def test_no_peak_periods_configured_is_the_same_as_none_supplied():
    """The empty default (nothing configured yet) behaves identically to
    ``None`` — a caller should not have to know which one the config uses."""
    assert _check(on=date(2026, 9, 1), peaks=[]).is_peak is False
    assert _check(on=date(2026, 9, 1), peaks=None).is_peak is False


def test_peak_period_covering_reports_the_first_match():
    early = PeakPeriod(start=date(2026, 1, 1), end=date(2026, 1, 10), label="A")
    late = PeakPeriod(start=date(2026, 1, 5), end=date(2026, 1, 20), label="B")
    found = peak_period_covering(date(2026, 1, 6), [early, late])
    assert found is not None
    assert found.label == "A"


# --------------------------------------------------------------------------- #
# Small pieces
# --------------------------------------------------------------------------- #


def test_notice_days_counts_whole_days():
    assert notice_days(departure_date=date(2026, 12, 1), notice_on=date(2026, 9, 1)) == 91


def test_a_negative_total_is_refused():
    with pytest.raises(ValueError):
        check_cancellation(
            total_amount=D("-1"),
            departure_date=DEPARTURE,
            notice_on=date(2026, 9, 1),
            pax_count=2,
            is_exclusive_use=False,
            deposit_pct=D("30"),
            tier1_days=90,
            tier2_days=60,
            tier2_pct=D("50"),
            tier3_days=30,
            tier3_pct=D("75"),
            forfeit_pct=D("100"),
            group_pax_threshold=8,
            group_notice_extension_days=30,
        )


def test_a_cancellation_is_frozen_data_not_a_live_object():
    """Comparable and hashable-shaped like every other pure result in this
    codebase, so a test can assert equality directly."""
    a = _check(on=date(2026, 9, 1))
    b = _check(on=date(2026, 9, 1))
    assert a == b
    assert isinstance(a, Cancellation)


# --------------------------------------------------------------------------- #
# Settling a cancellation: refund, or still owed
# --------------------------------------------------------------------------- #


def test_more_paid_than_retained_is_a_refund():
    """Deposit-only retained (30%), full amount already paid: 70% comes back."""
    found = settle_cancellation(retained_amount=D("60000"), paid_amount=D("200000"))
    assert found.refund_due == D("140000")
    assert found.still_owed == D("0")


def test_less_paid_than_retained_is_still_owed():
    """Cancelled at 63 days' notice (50% retained) with only the 30% deposit
    paid so far: the client owes the missing 20%, not nothing.

    This is the exact failure this module exists to prevent: a business that
    read "the deposit is non-refundable anyway" as "there is nothing more to
    collect" would quietly under-charge every cancellation like this one.
    """
    found = settle_cancellation(retained_amount=D("100000"), paid_amount=D("60000"))
    assert found.still_owed == D("40000")
    assert found.refund_due == D("0")


def test_paid_exactly_what_is_retained_settles_at_zero():
    found = settle_cancellation(retained_amount=D("60000"), paid_amount=D("60000"))
    assert found.refund_due == D("0")
    assert found.still_owed == D("0")


def test_nothing_paid_at_all_is_the_whole_retained_amount_still_owed():
    found = settle_cancellation(retained_amount=D("60000"), paid_amount=D("0"))
    assert found.still_owed == D("60000")


def test_settlement_refuses_a_negative_input():
    with pytest.raises(ValueError):
        settle_cancellation(retained_amount=D("-1"), paid_amount=D("0"))
    with pytest.raises(ValueError):
        settle_cancellation(retained_amount=D("0"), paid_amount=D("-1"))
