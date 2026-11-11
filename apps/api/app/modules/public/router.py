"""The public surface (§6.1).

**Every route under ``/public`` is unauthenticated.** That is a first for this
platform and the reason this module is worth reading before adding to it.
Three rules hold the boundary, and none of them is "remember to be careful":

1. Nothing is visible until somebody publishes it. ``is_published`` defaults
   to false on every row that exists and every row created from now on.
2. What a published row shows is an allow-list, not the row minus some
   columns (:mod:`app.modules.public.site`).
3. Everything is rate-limited, including the reads. A public read endpoint
   with no limit is a free denial-of-service tool aimed at the database that
   also runs the quote engine.

There is exactly one write: the enquiry form. It creates a lead at the arrival
stage with no owner and no value, and it cannot touch anything else.

``/public/estimate`` (§6.3) is a second kind of route: it computes rather than
writes, and it is the one place this surface produces a **price**. §6.1 held
the line that nothing here should — every real figure depends on dates, party
shape, residence and season, and a published one is a promise. The client has
since asked for a computed number the builder can show, so this endpoint gives
one honestly: real published rates, the real build-up arithmetic, and every
simplification it makes said out loud in the response rather than hidden in
the figure. See :mod:`app.modules.public.estimate`.

No CORS is configured, and that is not an omission. ``apps/web`` talks to this
through its own server-side routes, the way ``apps/admin`` and ``apps/portal``
do, so no browser ever addresses this API directly and no origin needs to be
allowed. Adding a wildcard origin here to make a fetch work from a browser
would undo that in one line.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import require_permission
from app.core.limits import rate_limit
from app.core.storage import resolve
from app.db.session import get_db
from app.modules.public.enquiry import Submitted
from app.modules.public.schemas import (
    ContactRead,
    EnquiryCreate,
    EnquiryReceived,
    EstimateRead,
    EstimateRequest,
    ExperienceRead,
    LegEstimateRead,
    PlaceRead,
    PropertyRead,
    PublishedRead,
    PublishResult,
    ThinPageRead,
)
from app.modules.public.service import (
    DESTINATION,
    PROPERTY,
    EnquiryService,
    EstimateService,
    PublicSiteService,
    PublishService,
)
from app.modules.users.models import User

router = APIRouter(tags=["public"])

#: Its own permission. Putting a property on the business's website is not the
#: same act as loading its rates, and it is frequently not the same person:
#: whoever does the marketing needs this and has no business editing a
#: contract rate, while whoever loads rate sheets should not be able to
#: advertise forty hotels by accident.
PUBLISH = "catalogue:publish"

_reads = Depends(
    rate_limit(
        bucket="public_read",
        limit=settings.PUBLIC_READ_PER_MINUTE,
        seconds=60,
    )
)
_enquiries = Depends(
    rate_limit(
        bucket="public_enquiry",
        limit=settings.PUBLIC_ENQUIRIES_PER_HOUR,
        seconds=3600,
    )
)
_estimates = Depends(
    rate_limit(
        bucket="public_estimate",
        limit=settings.PUBLIC_ESTIMATES_PER_HOUR,
        seconds=3600,
    )
)


# --------------------------------------------------------------------------- #
# What the world may read
# --------------------------------------------------------------------------- #


@router.get("/public/contact", response_model=ContactRead, dependencies=[_reads])
async def public_contact(db: AsyncSession = Depends(get_db)):
    """How to reach the business — one source, the same one the quotation
    document prints, so the website and a client's own document never disagree."""
    return await PublicSiteService(db).contact()


@router.get("/public/destinations", response_model=list[PlaceRead], dependencies=[_reads])
async def public_destinations(db: AsyncSession = Depends(get_db)):
    """Every published destination. The index page of a website."""
    return await PublicSiteService(db).places()


@router.get("/public/destinations/{slug}", response_model=PlaceRead, dependencies=[_reads])
async def public_destination(slug: str, db: AsyncSession = Depends(get_db)):
    """One destination, with its photographs and what is published there.

    Addressed by **slug**, not id. A URL is part of the page: it is what gets
    shared, printed and indexed, and a UUID in it is a URL nobody types twice.
    """
    return await PublicSiteService(db).place(slug)


@router.get(
    "/public/accommodations", response_model=list[PropertyRead], dependencies=[_reads]
)
async def public_properties(
    destination: str | None = Query(default=None, description="Destination slug"),
    db: AsyncSession = Depends(get_db),
):
    return await PublicSiteService(db).properties(destination=destination)


@router.get(
    "/public/accommodations/{slug}", response_model=PropertyRead, dependencies=[_reads]
)
async def public_property(slug: str, db: AsyncSession = Depends(get_db)):
    return await PublicSiteService(db).property_page(slug)


@router.get(
    "/public/activities", response_model=list[ExperienceRead], dependencies=[_reads]
)
async def public_activities(
    destination: str | None = Query(default=None, description="Destination slug"),
    db: AsyncSession = Depends(get_db),
):
    return await PublicSiteService(db).experiences(destination=destination)


@router.get("/public/images/{kind}/{image_id}", dependencies=[_reads])
async def public_image(
    kind: str, image_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """One photograph, if what it belongs to is published.

    The parent check is the whole endpoint. Without it this would be an
    unauthenticated read of every image in the system — including the ones on
    a property nobody has decided to advertise — and an id is not a secret.

    Cached hard, because these rows are immutable: an image is replaced by
    uploading another one and deleting this, never by editing it in place.
    """
    image = await PublicSiteService(db).image(kind, image_id)
    return FileResponse(
        resolve(image.storage_path),
        media_type=image.content_type,
        headers={"Cache-Control": "public, max-age=604800, immutable"},
    )


# --------------------------------------------------------------------------- #
# The one write
# --------------------------------------------------------------------------- #


@router.post(
    "/public/enquiries",
    response_model=EnquiryReceived,
    status_code=202,
    dependencies=[_enquiries],
)
async def submit_enquiry(body: EnquiryCreate, db: AsyncSession = Depends(get_db)):
    """The contact form. Becomes a lead and a logged inbound message.

    **202, not 201**, and the response carries no reference. Accepted is the
    honest answer: what happens next is a person reading it, and a created-id
    would be a lookup key into the sales pipeline handed to whoever asked.

    The same answer comes back whether the enquiry was recorded or dropped as
    spam. See ``check_enquiry`` on the trap field for why that is worth the
    one lie in this codebase.
    """
    await EnquiryService(db).capture(
        Submitted(
            name=body.name,
            email=body.email,
            phone=body.phone,
            destination=body.destination,
            travel_from=body.travel_from,
            travel_to=body.travel_to,
            pax=body.pax,
            message=body.message,
            page=body.page,
            trap=body.trap,
        )
    )
    return EnquiryReceived()


@router.post(
    "/public/estimate",
    response_model=EstimateRead,
    dependencies=[_estimates],
)
async def estimate_trip(body: EstimateRequest, db: AsyncSession = Depends(get_db)):
    """An indicative price for a trip nobody has booked yet.

    Never a quote: it carries no reference, is never issued, and expresses no
    validity period — none of §3.4's own markers for the document a client can
    actually accept. A leg that cannot be priced honestly comes back refused
    rather than guessed, and the whole trip is only totalled once every leg
    priced and shares one currency (see ``public.estimate.combine`` on why a
    mixed-currency trip is reported per leg instead of summed).
    """
    legs, combined = await EstimateService(db).price_trip(
        [(leg.destination, leg.tier, leg.nights) for leg in body.legs],
        resident=body.resident,
        adults=body.adults,
        children=body.children,
    )
    return EstimateRead(
        legs=[
            LegEstimateRead(
                destination=leg.destination,
                tier=leg.tier,
                nights=leg.nights,
                property_name=leg.property_name,
                room_type=leg.room_type,
                meal_plan=leg.meal_plan,
                currency=leg.currency,
                per_person=leg.per_person,
                group_total=leg.group_total,
                refused=leg.refused.message if leg.refused else None,
            )
            for leg in legs
        ],
        currency=combined.currency,
        per_person=combined.per_person,
        group_total=combined.group_total,
    )


# --------------------------------------------------------------------------- #
# Staff: deciding what is public
# --------------------------------------------------------------------------- #


@router.post("/catalogue/{kind}/{row_id}/publish", response_model=PublishResult)
async def publish(
    kind: str,
    row_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(require_permission(PUBLISH)),
):
    """Put one destination, property or activity on the website.

    Refused if it cannot be sold or has no copy; anything else that will look
    thin comes back in ``concerns`` rather than blocking it.
    """
    row, concerns = await PublishService(db).publish(kind, row_id, actor_id=actor.id)
    return PublishResult(
        **PublishedRead.model_validate(row).model_dump(),
        concerns=[{"code": one.code, "message": one.message} for one in concerns],
    )


@router.post("/catalogue/{kind}/{row_id}/withdraw", response_model=PublishedRead)
async def withdraw(
    kind: str,
    row_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PUBLISH)),
):
    """Take it off the website. The row is untouched otherwise."""
    return await PublishService(db).withdraw(kind, row_id)


@router.get("/catalogue/{kind}/thin-pages", response_model=list[ThinPageRead])
async def thin_pages(
    kind: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PUBLISH)),
):
    """Live pages that need work — the website's version of the morning list.

    A page published before its photographs arrived, and text on a white
    background ever since, is not something anybody would notice on their own.
    """
    found = await PublishService(db).review(kind)
    return [
        ThinPageRead(
            id=row.id,
            name=row.name,
            slug=row.slug,
            concerns=[{"code": one.code, "message": one.message} for one in concerns],
        )
        for row, concerns in found
    ]


__all__ = ["router", "PUBLISH", "DESTINATION", "PROPERTY"]
