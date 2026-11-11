"""What a cancellation costs, once somebody actually says (§2.1).

Until 2026-09-13 nothing here computed a charge at all — the ladder was
commercial policy nobody had given us, and a plausible invented figure on a
refund reads exactly like one that came from a contract, which is a worse
mistake than an empty field. The client has since confirmed a ladder (see
``docs/cancellation-policy-draft.md`` for the policy in the client's own
words); this module is that ladder, as arithmetic.

**Measured in days' notice before departure, against the total trip cost —
not the deposit alone.** A booking cancelled at 70 days' notice with only the
deposit paid so far can still owe *more* than has been paid in: the ladder
says what fraction of the whole trip is retained, and comparing that against
what has actually landed in ``payments`` is a separate question this module
does not answer (see ``BookingService.cancel`` and ``.settlement``) — a
refund and a debt are both real outcomes of the same rule, and conflating
them here would hide whichever one a caller was not expecting.

**Peak dates override the ladder entirely, not add to it.** Where a
property's own terms are non-refundable from the moment of booking, the
notice given is beside the point — see :class:`app.modules.pricing.config.
PeakPeriodConfig` on why those dates are reference data an admin maintains
rather than a date computed here.

**A group or an exclusive-use booking gets the same ladder, later.** Every
day threshold is pushed back by the same extension, rather than a separate
set of percentages — the client's own shape for it ("the same ladder, but at
120/90/60 days"), and one that keeps the two ladders from silently drifting
apart into two different policies.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

#: Deposit only — the top band, named for what it costs rather than a number,
#: because that number is ``deposit_pct`` and lives in pricing config, not here.
TIER_DEPOSIT_ONLY = "deposit_only"
TIER_SECOND = "second_tier"
TIER_THIRD = "third_tier"
#: Also reached by a genuine no-show: a departure date already in the past
#: gives a negative day-count, which falls into this band along with everything
#: under the third tier's threshold, with no separate check needed for it.
TIER_FORFEIT = "forfeit"
TIER_PEAK = "peak_period"


@dataclass(frozen=True)
class PeakPeriod:
    """A date range as the rule sees it — not the config row.

    A plain tuple-shaped dataclass rather than importing ``PeakPeriodConfig``
    directly: this module stays free of any dependency on how the config is
    stored, the same separation every other pure module in this codebase
    keeps from its service layer.
    """

    start: date
    end: date
    label: str = ""

    def covers(self, day: date) -> bool:
        return self.start <= day <= self.end


@dataclass(frozen=True)
class Cancellation:
    """What the ladder says about one cancellation, and why."""

    notice_days: int
    band: str
    is_peak: bool
    is_group: bool
    retained_pct: Decimal
    retained_amount: Decimal
    peak_label: str = ""


def notice_days(*, departure_date: date, notice_on: date) -> int:
    """Whole days between the notice and the departure date.

    Negative where the departure date has already passed — a no-show is not a
    special case this needs to check for separately; it simply falls further
    below every threshold than a late cancellation does, landing in the same
    forfeit band.
    """
    return (departure_date - notice_on).days


def peak_period_covering(
    departure_date: date, periods: list[PeakPeriod]
) -> PeakPeriod | None:
    """The peak period this trip falls in, if any. First match wins.

    Overlapping periods in the configured list are the admin's problem to
    tidy up, not this function's to adjudicate — it answers honestly for
    whichever one it is handed first rather than silently picking a "right"
    one between two the config should not have contained.
    """
    for period in periods:
        if period.covers(departure_date):
            return period
    return None


def check_cancellation(
    *,
    total_amount: Decimal,
    departure_date: date,
    notice_on: date,
    pax_count: int,
    is_exclusive_use: bool,
    deposit_pct: Decimal,
    tier1_days: int,
    tier2_days: int,
    tier2_pct: Decimal,
    tier3_days: int,
    tier3_pct: Decimal,
    forfeit_pct: Decimal,
    group_pax_threshold: int,
    group_notice_extension_days: int,
    peak_periods: list[PeakPeriod] | None = None,
) -> Cancellation:
    """What is retained if this booking is cancelled today.

    A pure question with no side effect and no opinion on what happens next —
    it does not touch a booking row, and it does not know what has already
    been paid. ``BookingService.cancel`` is where this meets a real booking.
    """
    if total_amount < 0:
        raise ValueError("total_amount cannot be negative")
    tiers = (("tier1_days", tier1_days), ("tier2_days", tier2_days), ("tier3_days", tier3_days))
    for name, days in tiers:
        if days < 0:
            raise ValueError(f"{name} cannot be negative")

    days = notice_days(departure_date=departure_date, notice_on=notice_on)
    is_group = pax_count >= group_pax_threshold or is_exclusive_use
    extension = group_notice_extension_days if is_group else 0

    peak = peak_period_covering(departure_date, peak_periods or [])
    if peak is not None:
        band, pct = TIER_PEAK, forfeit_pct
    elif days >= tier1_days + extension:
        band, pct = TIER_DEPOSIT_ONLY, deposit_pct
    elif days >= tier2_days + extension:
        band, pct = TIER_SECOND, tier2_pct
    elif days >= tier3_days + extension:
        band, pct = TIER_THIRD, tier3_pct
    else:
        band, pct = TIER_FORFEIT, forfeit_pct

    retained = (total_amount * pct / Decimal(100)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return Cancellation(
        notice_days=days,
        band=band,
        is_peak=peak is not None,
        is_group=is_group,
        retained_pct=pct,
        retained_amount=retained,
        peak_label=peak.label if peak else "",
    )


@dataclass(frozen=True)
class Settlement:
    """Whether a cancelled booking is owed a refund or still owes money.

    Both are real outcomes of the same rule, and exactly one of them is ever
    non-zero: the ladder decides what fraction of the trip the business
    keeps, entirely independent of how much has actually landed in
    ``payments`` so far. A booking cancelled at 70 days' notice with only the
    30% deposit paid, on a ladder that retains 50% at that notice, owes a
    further 20% — it does not "already owe nothing because the deposit was
    non-refundable anyway". Conflating the two is how a business quietly
    under-collects on a cancellation it was entitled to charge for.
    """

    retained_amount: Decimal
    paid_amount: Decimal
    refund_due: Decimal
    still_owed: Decimal


def settle_cancellation(
    *, retained_amount: Decimal, paid_amount: Decimal
) -> Settlement:
    """Compare what the ladder retains against what has actually been paid.

    Deliberately separate from :func:`check_cancellation`: the ladder's
    decision does not depend on what has been paid, and folding the two
    together would make it look as though a client's own payment history
    could change what the business is entitled to retain. It cannot — it
    only changes whether that entitlement is still owed or has already been
    covered.
    """
    if retained_amount < 0:
        raise ValueError("retained_amount cannot be negative")
    if paid_amount < 0:
        raise ValueError("paid_amount cannot be negative")
    return Settlement(
        retained_amount=retained_amount,
        paid_amount=paid_amount,
        refund_due=max(paid_amount - retained_amount, Decimal(0)),
        still_owed=max(retained_amount - paid_amount, Decimal(0)),
    )


__all__ = [
    "TIER_DEPOSIT_ONLY",
    "TIER_FORFEIT",
    "TIER_PEAK",
    "TIER_SECOND",
    "TIER_THIRD",
    "Cancellation",
    "PeakPeriod",
    "Settlement",
    "check_cancellation",
    "notice_days",
    "peak_period_covering",
    "settle_cancellation",
]
