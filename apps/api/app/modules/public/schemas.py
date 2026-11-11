"""Schemas for the public surface (§6.1).

The read models mirror :mod:`app.modules.public.site`'s allow-list rather than
the catalogue tables. That is deliberate duplication: a response model built
from the ORM row with ``from_attributes`` would gain every column the table
gains, which is exactly the failure the allow-list exists to prevent.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.public.enquiry import MAX_MESSAGE, MAX_NAME, MAX_PAX


class ImageRead(BaseModel):
    id: str
    url: str
    alt_text: str | None = None
    width: int | None = None
    height: int | None = None
    #: The hero on a property, the cover on a destination.
    is_lead: bool = False


class PlaceRead(BaseModel):
    name: str
    slug: str
    type: str = ""
    country: str = ""
    region: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    description: str | None = None
    images: list[ImageRead] = Field(default_factory=list)
    #: Names only. A visitor following one of these gets the property's own
    #: page; embedding the whole property here would put the same paragraph in
    #: two responses and double what a page change has to keep in step.
    stays: list[str] = Field(default_factory=list)
    activities: list[str] = Field(default_factory=list)


class PropertyRead(BaseModel):
    name: str
    slug: str
    category: str = ""
    star_rating: int | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    check_in_time: str | None = None
    check_out_time: str | None = None
    #: The proposal ``blurb``, under the name a reader would use.
    description: str | None = None
    destination: str = ""
    destination_slug: str = ""
    #: Room names and occupancy. No rate, and **no availability** — this
    #: system has never modelled availability, and a website that implied
    #: otherwise would be lying in the most expensive way available.
    rooms: list[str] = Field(default_factory=list)
    images: list[ImageRead] = Field(default_factory=list)


class ContactRead(BaseModel):
    """How to reach the business, for the website's contact page and footer.

    An allow-list over ``DocumentConfig`` (§3.6) — the same config the
    quotation document prints, and the reason nothing here is invented: a
    phone number typed into a page template is the one that goes stale and
    the one a client rings, so the website reads the same single source of
    truth the client-facing documents already do.
    """

    company_name: str
    contact_email: str
    contact_phone: str
    social_line: str


class ExperienceRead(BaseModel):
    name: str
    slug: str
    description: str | None = None
    duration_minutes: int | None = None
    destination: str = ""
    destination_slug: str = ""


# --------------------------------------------------------------------------- #
# Enquiries
# --------------------------------------------------------------------------- #


class EnquiryCreate(BaseModel):
    """The website contact form.

    Only ``name`` plus one of email/phone is really required; everything else
    is optional because an enquiry that says "August, two of us, somewhere with
    a beach" is the most valuable kind and no form should refuse it.
    """

    name: str = Field(max_length=MAX_NAME)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    destination: str | None = Field(default=None, max_length=200)
    travel_from: date | None = None
    travel_to: date | None = None
    pax: int | None = Field(default=None, ge=1, le=MAX_PAX)
    message: str | None = Field(default=None, max_length=MAX_MESSAGE)
    #: Which page or campaign it came from.
    page: str | None = Field(default=None, max_length=200)
    #: A field a browser never shows a person. Named for what it is rather
    #: than disguised as something plausible: the disguise belongs in the
    #: markup, and a schema that lied here would be a trap for the next
    #: developer instead of a bot.
    trap: str | None = Field(default=None, max_length=200)

    #: No budget field, deliberately. See the module docstring of
    #: app/modules/public/enquiry.py: a figure with no currency beside it is
    #: not money, and guessing the currency from the site's country is how a
    #: European family's real budget gets read as a hundredth of itself.


class EnquiryReceived(BaseModel):
    """What the form gets back. Never the lead.

    A reference would be a lookup key for something a stranger has no business
    reading, and the id of a lead is the id of a row in the sales pipeline.
    The answer is an acknowledgement and nothing else — and it is the same
    acknowledgement whether the enquiry was recorded or dropped as spam.
    """

    received: bool = True
    message: str = (
        "Thank you — your enquiry has reached us and somebody will be in touch."
    )


# --------------------------------------------------------------------------- #
# Publishing (staff)
# --------------------------------------------------------------------------- #


class ConcernRead(BaseModel):
    code: str
    message: str


class PublishedRead(BaseModel):
    """A row's publication state, for whoever pressed the button."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    is_published: bool
    published_at: datetime | None = None
    published_by: uuid.UUID | None = None


class PublishResult(PublishedRead):
    """Published, plus what will look thin. See PublishService.publish."""

    concerns: list[ConcernRead] = Field(default_factory=list)


class ThinPageRead(BaseModel):
    """One live page that needs work, for the review list."""

    id: uuid.UUID
    name: str
    slug: str
    concerns: list[ConcernRead] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# The safari builder's indicative estimate (§6.3)
# --------------------------------------------------------------------------- #


class LegRequest(BaseModel):
    #: A destination slug, as the public catalogue names it.
    destination: str = Field(max_length=220)
    tier: str = Field(max_length=20)
    nights: int = Field(ge=1, le=30)


class EstimateRequest(BaseModel):
    resident: bool = False
    adults: int = Field(ge=1, le=20)
    #: Priced as adults — see app/modules/public/estimate.py on why a
    #: discount is not invented here.
    children: int = Field(default=0, ge=0, le=10)
    legs: list[LegRequest] = Field(min_length=1, max_length=6)


class LegEstimateRead(BaseModel):
    """One leg, priced — or the reason it could not be, never both."""

    destination: str
    tier: str
    nights: int
    property_name: str | None = None
    room_type: str | None = None
    meal_plan: str | None = None
    currency: str | None = None
    per_person: Decimal | None = None
    group_total: Decimal | None = None
    refused: str | None = None


class EstimateRead(BaseModel):
    """The whole trip. Never called a quote — see the module docstring."""

    legs: list[LegEstimateRead]
    #: ``None`` unless every leg priced and shares one currency (see
    #: EstimateService.price_trip / public.estimate.combine).
    currency: str | None = None
    per_person: Decimal | None = None
    group_total: Decimal | None = None
    note: str = (
        "Indicative only, based on rates published for today rather than your "
        "actual travel dates. A consultant confirms every figure — including "
        "child pricing, transfers and park fees, none of which are in this "
        "total — before you pay anything."
    )
