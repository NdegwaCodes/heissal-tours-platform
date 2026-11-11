"""An indicative price for a stranger's own trip. Pure rules (§6.3).

§6.1 refused to put a price anywhere on the public site: every real figure this
engine produces depends on dates, party shape, residence category and season,
and a published "from" price is a promise the business would have to honour
or explain. The client has now asked for the opposite of that caution — the
safari builder should show a computed number — which is a different question
from whether one *can* be computed honestly. It can, from the same rates and
the same build-up arithmetic the real quote engine uses (:mod:`app.modules.
quotes.options`); this module reuses that arithmetic rather than re-deriving
it, and narrows where it must rather than guessing.

**What is simplified, and said out loud rather than hidden:**

* **One snapshot date, not a stay.** The builder collects no travel dates —
  only nights per destination — so every leg is priced off whatever rate is
  active *today*. The real engine prices every night of an actual stay
  individually (a booking crossing into a festive window is not priced at the
  cheaper season); this cannot, because it does not know when the stay is.
  The response says so, and the enquiry that follows carries real dates.
* **One representative property per destination and comfort tier**, chosen as
  the cheapest published, active match — never an invented name, and never a
  named property that has no active rate to back the figure.
* **A child is priced as an adult.** Child pricing is a fact about one
  property's rate row (``child_rate``, ``child_min_age``/``child_max_age``),
  not a rule this module can safely default — CLAUDE.md's own line on
  child-age rules. Charging the adult rate is the direction that cannot
  under-quote; the response says a child's real rate is confirmed with the
  quotation.
* **No transfers, flights or park fees.** Each is priced against the exact
  route or park a consultant fixes, and none has an honest per-destination
  flat figure to show here without it. Naming a number for them would be
  inventing exactly the kind of business figure CLAUDE.md forbids hard-coding.

Nothing here is a quote, an offer, or anything a client has accepted (§3.4's
own words for that document). It is an indication, and every response repeats
that in the client's own words.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.modules.quotes.options import rate_for_occupancy, room_plan

#: Star-rating bands for the three comfort levels the builder offers. Our own
#: presentational grouping, not something the client stated — an unrated
#: property (``star_rating`` is ``None``) matches none of them rather than
#: being guessed into one, because a tier promise ("Luxury") is a promise
#: about the property and not one this module can make on a rating nobody set.
TIER_BANDS: dict[str, tuple[int, int]] = {
    "comfort": (1, 3),
    "luxury": (4, 4),
    "ultra": (5, 5),
}

#: Every room in the plan is priced from this size, matching the real engine's
#: §3.3 default: a couple's double is the unit a trip is built around, and an
#: uneven party pays a full-price single for whatever is left over rather than
#: half a double it is not occupying.
ROOM_CAPACITY = 2

NO_TIER = "estimate_unknown_tier"
NO_PROPERTY = "estimate_no_property"
NO_RATE = "estimate_no_rate"


class EstimateRefused(Exception):
    """This leg cannot be priced honestly, with something a visitor can act on."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def star_band(tier: str) -> tuple[int, int]:
    key = (tier or "").strip().lower()
    if key not in TIER_BANDS:
        raise EstimateRefused(
            NO_TIER,
            f"'{tier}' is not a comfort level we offer. Choose comfort, luxury "
            f"or ultra.",
        )
    return TIER_BANDS[key]


@dataclass(frozen=True)
class LegPriced:
    """One leg of the trip, priced — or the reason it could not be."""

    destination: str
    tier: str
    nights: int
    property_name: str | None = None
    room_type: str | None = None
    meal_plan: str | None = None
    currency: str | None = None
    per_person: Decimal | None = None
    group_total: Decimal | None = None
    refused: EstimateRefused | None = None

    @property
    def ok(self) -> bool:
        return self.refused is None


def price_rooms(
    rates_by_occupancy: dict[int, Decimal], *, pax: int
) -> Decimal | None:
    """The night's accommodation cost for ``pax`` guests, room by room.

    ``room_plan`` says how many people share each room — full doubles first,
    one part-filled room last, priced at whatever the sheet charges for that
    many guests (never halved: there is no honest way to sell half a filed
    room-night). ``None`` only where a room in the plan needs an occupancy the
    property has filed nothing for at all, which :func:`rate_for_occupancy`
    cannot report, so the whole leg is refused rather than silently dropped.
    """
    total = Decimal(0)
    for headcount in room_plan(pax, ROOM_CAPACITY):
        found = rate_for_occupancy(rates_by_occupancy, headcount)
        if found is None:
            return None
        _, rate = found
        total += rate
    return total


@dataclass(frozen=True)
class Combined:
    """The whole trip, once every leg has its own figure.

    ``currency`` is ``None`` — and so are the totals — the moment two legs
    price in different currencies. Summing across them would be exactly the
    error this platform refuses everywhere else (§7.1, §8.3): what a Diani
    beach cottage charges in shillings and a Laikipia camp charges in dollars
    are two facts, not one number.
    """

    currency: str | None
    per_person: Decimal | None
    group_total: Decimal | None
    mixed_currency: bool = False


def combine(legs: list[LegPriced]) -> Combined:
    priced = [leg for leg in legs if leg.ok]
    if not priced or len(priced) != len(legs):
        return Combined(currency=None, per_person=None, group_total=None)
    currencies = {leg.currency for leg in priced}
    if len(currencies) > 1:
        return Combined(
            currency=None, per_person=None, group_total=None, mixed_currency=True
        )
    currency = currencies.pop()
    per_person = sum((leg.per_person or Decimal(0) for leg in priced), Decimal(0))
    group_total = sum((leg.group_total or Decimal(0) for leg in priced), Decimal(0))
    return Combined(currency=currency, per_person=per_person, group_total=group_total)


__all__ = [
    "NO_PROPERTY",
    "NO_RATE",
    "NO_TIER",
    "ROOM_CAPACITY",
    "TIER_BANDS",
    "Combined",
    "EstimateRefused",
    "LegPriced",
    "combine",
    "price_rooms",
    "star_band",
]
