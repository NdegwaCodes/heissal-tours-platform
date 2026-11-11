from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.pricing.config import PeakPeriodConfig


class PricingConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    default_markup_pct: Decimal
    default_tax_pct: Decimal
    default_discount_pct: Decimal
    discount_approval_threshold_pct: Decimal
    max_discount_pct: Decimal
    quote_validity_days: int

    # --- Stage 3 quotation build-up and quote shape ------------------------ #
    # Exposed because the design doc requires them to be an admin edit rather
    # than a deploy: "profit is a fixed 24% ... it lives in the existing
    # app_settings pricing config (not hard-coded), with a per-quote override for
    # the exception case" (§3.6). Left out of the schema they were configurable in
    # name only.
    contingency_pct: Decimal
    profit_pct: Decimal
    per_person_rounding: Decimal
    per_person_rounding_by_currency: dict[str, Decimal]
    quotation_validity_days: int
    min_catered_options: int
    max_catered_options: int
    min_self_catering_options: int
    max_self_catering_options: int
    # How much driving this operation will sell in a day (§4.3). Exposed for
    # the reason every other threshold here is: configurable in name only is
    # not configurable.
    max_drive_minutes_per_day: int
    # The standing chef-fee default (§3.4, 2026-09-13): a day rate, one chef
    # per this many guests, regardless of how many meals that day the plan
    # leaves uncovered. See quotes.options.default_chef_fee_per_meal for the
    # conversion into the schema's own per-meal shape.
    default_chef_fee_per_day: Decimal
    default_chef_covers: int
    # Booking terms (§7.1): what holds a trip, and when the rest is due.
    deposit_pct: Decimal
    balance_due_days_before_travel: int
    # The cancellation ladder (§2.1). See PricingConfig's own comment on why
    # the top band has no separate percentage of its own here.
    cancellation_tier1_days: int
    cancellation_tier2_days: int
    cancellation_tier2_pct: Decimal
    cancellation_tier3_days: int
    cancellation_tier3_pct: Decimal
    cancellation_forfeit_pct: Decimal
    cancellation_group_pax_threshold: int
    cancellation_group_notice_extension_days: int
    cancellation_peak_periods: list[PeakPeriodConfig]


class PricingConfigUpdate(BaseModel):
    """Partial update — only the provided fields are changed."""

    default_markup_pct: Decimal | None = Field(default=None, ge=0)
    default_tax_pct: Decimal | None = Field(default=None, ge=0)
    default_discount_pct: Decimal | None = Field(default=None, ge=0, le=100)
    discount_approval_threshold_pct: Decimal | None = Field(default=None, ge=0, le=100)
    max_discount_pct: Decimal | None = Field(default=None, ge=0, le=100)
    quote_validity_days: int | None = Field(default=None, ge=1)
    contingency_pct: Decimal | None = Field(default=None, ge=0, le=100)
    profit_pct: Decimal | None = Field(default=None, ge=0, le=100)
    per_person_rounding: Decimal | None = Field(default=None, gt=0)
    # Replaces the whole map when sent — a per-currency step is a policy, and
    # merging keys would leave a removed currency silently in force.
    per_person_rounding_by_currency: dict[str, Decimal] | None = None
    quotation_validity_days: int | None = Field(default=None, ge=1)
    min_catered_options: int | None = Field(default=None, ge=1)
    max_catered_options: int | None = Field(default=None, ge=1)
    min_self_catering_options: int | None = Field(default=None, ge=0)
    max_self_catering_options: int | None = Field(default=None, ge=0)
    max_drive_minutes_per_day: int | None = Field(default=None, ge=60)
    default_chef_fee_per_day: Decimal | None = Field(default=None, ge=0)
    default_chef_covers: int | None = Field(default=None, ge=1)
    deposit_pct: Decimal | None = Field(default=None, gt=0, le=100)
    balance_due_days_before_travel: int | None = Field(default=None, ge=0)
    cancellation_tier1_days: int | None = Field(default=None, ge=0)
    cancellation_tier2_days: int | None = Field(default=None, ge=0)
    cancellation_tier2_pct: Decimal | None = Field(default=None, ge=0, le=100)
    cancellation_tier3_days: int | None = Field(default=None, ge=0)
    cancellation_tier3_pct: Decimal | None = Field(default=None, ge=0, le=100)
    cancellation_forfeit_pct: Decimal | None = Field(default=None, ge=0, le=100)
    cancellation_group_pax_threshold: int | None = Field(default=None, ge=1)
    cancellation_group_notice_extension_days: int | None = Field(default=None, ge=0)
    # Replaces the whole list when sent, same reasoning as the currency
    # rounding map above: a removed peak period silently staying in force
    # would be the opposite of what clearing it out was meant to do.
    cancellation_peak_periods: list[PeakPeriodConfig] | None = None


class ConversionRead(BaseModel):
    """Result of an FX conversion via the ExchangeRate service."""

    amount: Decimal
    from_currency: str
    to_currency: str
    on_date: str
    rate: Decimal
    converted: Decimal
