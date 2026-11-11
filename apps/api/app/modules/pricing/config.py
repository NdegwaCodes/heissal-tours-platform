"""PricingConfig — business-wide markup / discount / tax / validity defaults.

These are *configurable data*, not hard-coded business rules: they live in the
``app_settings`` table under the ``pricing`` key and are edited by admins/finance
via the API (master prompt §44 — "nothing hard-coded"). The values below are only
the initial defaults used the first time the config is read, before an admin has
saved any. Each field carries the percentages the pricing engine (Stage 2.8)
applies; a specific quote may still override them within approval limits.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

# The app_settings row key under which the pricing config JSON is stored.
PRICING_SETTINGS_KEY = "pricing"


class PeakPeriodConfig(BaseModel):
    """One date range where a cancellation forfeits everything (§2.1's ladder).

    Not computed. "The week either side of Easter" moves every year and
    "15 December to 5 January" crosses a year boundary — reference data an
    admin maintains, the same call already made for the KWS MICE ladder:
    shipped switched off until somebody who knows next year's dates enters
    them, rather than a guess baked into code that would be quietly wrong the
    first December it runs unattended.
    """

    start: date
    end: date
    label: str = ""


class PricingConfig(BaseModel):
    """Typed view over the ``pricing`` app-setting (all percentages are 0..100)."""

    model_config = ConfigDict(extra="ignore")

    default_markup_pct: Decimal = Field(default=Decimal("20"), ge=0)
    default_tax_pct: Decimal = Field(default=Decimal("0"), ge=0)
    default_discount_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    # A quote discount at or above this percentage requires manager approval.
    discount_approval_threshold_pct: Decimal = Field(default=Decimal("10"), ge=0, le=100)
    # Discounts above this hard ceiling are rejected outright.
    max_discount_pct: Decimal = Field(default=Decimal("30"), ge=0, le=100)
    # How long an issued quote stays valid, in days.
    quote_validity_days: int = Field(default=14, ge=1)

    # --- Stage 3 quotation build-up (design doc section 3.6) --------------- #
    # Contingency sits inside the cost basis, so it accrues profit.
    contingency_pct: Decimal = Field(default=Decimal("5"), ge=0, le=100)
    # Profit is a fixed 24% on the whole sum, confirmed by the client. It lives
    # here rather than in code so the exception case is an edit, not a deploy.
    profit_pct: Decimal = Field(default=Decimal("24"), ge=0, le=100)
    # The per-person figure is rounded UP to this step before being multiplied
    # back out to the group total, so the document's two headline numbers agree.
    # This is the fallback; the map below is what actually applies.
    per_person_rounding: Decimal = Field(default=Decimal("100"), gt=0)
    # **A step per currency.** One global step cannot be right for both: KES 100
    # is a rounding on a five-figure shilling price and a 48% mark-up on a
    # two-figure dollar one. Rounding USD 135 per person up to USD 200 does not
    # look like a rounding convention to a client, it looks like a different
    # quote — and it is the kind of error that loses a booking without anyone
    # learning why. USD 1 confirmed by the client 2026-09-04; the other foreign
    # currencies default to 1 for the same reason rather than waiting to be
    # discovered. Anything not listed falls back to ``per_person_rounding``.
    per_person_rounding_by_currency: dict[str, Decimal] = Field(
        default_factory=lambda: {
            "USD": Decimal("1"),
            "EUR": Decimal("1"),
            "GBP": Decimal("1"),
        }
    )
    # A Stage 3 quotation is valid for 30 days, unlike the Stage 2 default.
    quotation_validity_days: int = Field(default=30, ge=1)

    # --- Stage 3.4 quote shape (design doc §1, §3.7) ----------------------- #
    # "3-9 hotels plus 1-2 BnB options." Held as configurable bounds rather than
    # literals in a validator, and split by whether pricing had to add a chef —
    # the only distinction in the data that actually means "the guests feed
    # themselves". A property category string would not: it is free text.
    min_catered_options: int = Field(default=3, ge=1)
    max_catered_options: int = Field(default=9, ge=1)
    min_self_catering_options: int = Field(default=1, ge=0)
    max_self_catering_options: int = Field(default=2, ge=0)

    # --- Stage 4.3 itinerary sequencing ----------------------------------- #
    # How much driving this operation is willing to sell in one day. Ten hours
    # by default, which on Kenyan roads is a dawn start and an arrival before
    # the park gates shut. Configuration rather than a literal because it is a
    # commercial judgement about what Heissal will put in front of a client,
    # and the kind that changes the first time one complains.
    max_drive_minutes_per_day: int = Field(default=600, ge=60)

    # --- Stage 3.4 self-catering: the chef fee default (2026-09-13) -------- #
    # A self-catering or bed-and-breakfast option needs a chef and a manual
    # food cost, and until now both were typed by hand on every option — right
    # for a one-off, tedious for the common case. The client gave a standing
    # figure for the chef: KES 15,000 a day, one chef per six guests,
    # regardless of how many meals that day the plan leaves uncovered. It is
    # a day rate, not a per-meal one — the schema's chef_fee_per_meal is
    # divided back out of it (see quotes.options.default_chef_fee_per_meal)
    # only because pricing already multiplies that field by a meal count, not
    # because a chef is paid per meal.
    #
    # The food cost has no standing figure — the client gave one for the
    # chef only — so manual_meal_cost is still typed by hand, and an agent's
    # own chef_fee_per_meal still overrides this default when they set one.
    default_chef_fee_per_day: Decimal = Field(default=Decimal("15000"), ge=0)
    default_chef_covers: int = Field(default=6, ge=1)

    # --- Stage 7.1 booking terms ------------------------------------------- #
    # What a client pays to hold a trip, and when the rest is due. Commercial
    # terms, so they are config — and they are resolved to dated instalments at
    # the moment of booking, which is what freezes them: changing the deposit
    # rule next month must not restate an invoice already sent.
    deposit_pct: Decimal = Field(default=Decimal("30"), gt=0, le=100)
    balance_due_days_before_travel: int = Field(default=30, ge=0)

    # --- The cancellation ladder (§2.1, client-confirmed 2026-09-13) ------- #
    # Measured in days' notice before departure against the *total trip cost*,
    # not the deposit alone. The client's own words for the top band are
    # "deposit only" — so that band's retained figure is ``deposit_pct``
    # above, not a fourth number here that could quietly drift away from it.
    #
    #   90+ days notice   -> deposit_pct retained         (deposit only)
    #   60-89 days notice -> cancellation_tier2_pct        (default 50%)
    #   30-59 days notice -> cancellation_tier3_pct        (default 75%)
    #   under 30 / no-show -> cancellation_forfeit_pct     (default 100%)
    #
    # See app.modules.bookings.cancellation.check_cancellation for the rule
    # itself; this is only the numbers behind it.
    cancellation_tier1_days: int = Field(default=90, ge=0)
    cancellation_tier2_days: int = Field(default=60, ge=0)
    cancellation_tier2_pct: Decimal = Field(default=Decimal("50"), ge=0, le=100)
    cancellation_tier3_days: int = Field(default=30, ge=0)
    cancellation_tier3_pct: Decimal = Field(default=Decimal("75"), ge=0, le=100)
    # Kept as its own field rather than assumed, even though it is definitionally
    # "everything" — a business could choose a different final number, and a
    # figure this system refuses to guess should be just as visible here as the
    # other three.
    cancellation_forfeit_pct: Decimal = Field(default=Decimal("100"), ge=0, le=100)
    # A group, or a whole-property buyout, cannot be resold to someone else on
    # short notice the way a single room can — every threshold above is pushed
    # back by this many days once either condition is met.
    cancellation_group_pax_threshold: int = Field(default=8, ge=1)
    cancellation_group_notice_extension_days: int = Field(default=30, ge=0)
    # Empty until populated — see PeakPeriodConfig on why there is no sensible
    # default here.
    cancellation_peak_periods: list[PeakPeriodConfig] = Field(default_factory=list)

    def rounding_for(self, currency: str) -> Decimal:
        """The per-person rounding step for one currency.

        A method rather than a lookup at each call site: pricing rounds in three
        places (the option build-up, each cohort's own figure, and an optional
        add-on), and a fallback spelled out three times is a fallback that will
        eventually differ in one of them.
        """
        step = self.per_person_rounding_by_currency.get(currency.upper())
        if step is None or step <= 0:
            return self.per_person_rounding
        return step
