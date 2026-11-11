"""Publishing, the public read surface, and enquiry capture (§6.1)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, NotFoundError
from app.modules.accommodations.models import (
    Accommodation,
    AccommodationRate,
    MealPlan,
    RoomType,
)
from app.modules.activities.models import Activity
from app.modules.comms.models import LEAD
from app.modules.comms.rules import INBOUND
from app.modules.comms.service import CommsService
from app.modules.destinations.models import Destination
from app.modules.documents.service import DocumentConfigService
from app.modules.leads.models import Lead
from app.modules.leads.service import LeadService
from app.modules.media.models import DestinationImage, PropertyImage
from app.modules.narratives.service import property_copy
from app.modules.pricing.service import PricingConfigService
from app.modules.public.enquiry import (
    EnquiryRefused,
    Submitted,
    as_log_entry,
    check_enquiry,
)
from app.modules.public.estimate import (
    NO_PROPERTY,
    NO_RATE,
    ROOM_CAPACITY,
    Combined,
    EstimateRefused,
    LegPriced,
    combine,
    price_rooms,
    star_band,
)
from app.modules.public.schemas import ContactRead
from app.modules.public.site import (
    Candidate,
    Concern,
    Experience,
    Image,
    Place,
    Property,
    PublishRefused,
    check_page,
    check_publish,
    experience_of,
    place_of,
    property_of,
)
from app.modules.quotes.group import residence_ids
from app.modules.quotes.options import (
    build_up,
    rate_for_occupancy,
    resolve_meal_plan,
    room_plan,
)

logger = logging.getLogger("heissal.public")

#: The three things that can be published, and the model behind each. A string
#: rather than a class in the URL because these are page kinds a visitor would
#: recognise, not table names.
DESTINATION = "destination"
PROPERTY = "accommodation"
ACTIVITY = "activity"

_MODELS: dict[str, Any] = {
    DESTINATION: Destination,
    PROPERTY: Accommodation,
    ACTIVITY: Activity,
}


class PublishService:
    """Putting a catalogue row on the website, and taking it off again.

    Separate from the catalogue services on purpose: publishing is not an
    edit of the row's commercial data, it is a decision about the business's
    public face, and the person who makes it is often not the person who loads
    rates. It has its own permission for the same reason.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def publish(
        self, kind: str, row_id: uuid.UUID, *, actor_id: uuid.UUID | None = None
    ) -> tuple[Any, list[Concern]]:
        """Publish one row, or refuse with what is missing.

        Returns the row and anything thin about the page. The concerns are
        **returned rather than raised**: a property whose photographs arrive on
        Thursday is a real thing to publish on Wednesday, and a rule that
        blocked it would be worked around by publishing something worse.
        """
        kind = self._kind(kind)
        row = await self._get(kind, row_id)
        candidate = await self._candidate(kind, row)
        try:
            check_publish(candidate)
        except PublishRefused as exc:
            raise AppError(exc.message) from exc
        concerns = check_page(candidate, wants_rooms=kind == PROPERTY)

        row.is_published = True
        row.published_at = datetime.now(UTC)
        row.published_by = actor_id
        await self.db.commit()
        await self.db.refresh(row)
        return row, concerns

    async def withdraw(self, kind: str, row_id: uuid.UUID) -> Any:
        """Take one row off the website.

        No reason is required, unlike revoking a portal link (§7.2). Nobody is
        locked out and nobody has to be told why: a page comes down because a
        contract ended or the photographs were bad, and demanding a sentence
        for it would only train people to type a full stop.

        ``published_at`` and ``published_by`` are **left alone** — they record
        that this was once live, which is the question somebody asks when a
        search engine still has the page.
        """
        row = await self._get(kind, row_id)
        row.is_published = False
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def review(self, kind: str) -> list[tuple[Any, list[Concern]]]:
        """Every published row of this kind whose page is thin.

        The counterpart of §5.2's morning list, for the website: a page that
        went live before its photographs and has been text on a white
        background ever since is not something anybody would notice.
        """
        model = _MODELS[self._kind(kind)]
        rows = list(
            (
                await self.db.execute(select(model).where(model.is_published.is_(True)))
            )
            .scalars()
            .all()
        )
        out: list[tuple[Any, list[Concern]]] = []
        for row in rows:
            candidate = await self._candidate(self._kind(kind), row)
            found = check_page(candidate, wants_rooms=self._kind(kind) == PROPERTY)
            if found:
                out.append((row, found))
        return out

    # -- internals ---------------------------------------------------------- #

    @staticmethod
    def _kind(kind: str) -> str:
        key = (kind or "").strip().lower()
        if key not in _MODELS:
            raise NotFoundError(
                f"'{kind}' is not something that can be published. Expected one "
                f"of: {', '.join(sorted(_MODELS))}."
            )
        return key

    async def _get(self, kind: str, row_id: uuid.UUID) -> Any:
        model = _MODELS[self._kind(kind)]
        row = await self.db.get(model, row_id)
        if row is None:
            raise NotFoundError(f"No {self._kind(kind)} with that id.")
        return row

    async def _candidate(self, kind: str, row: Any) -> Candidate:
        """The row as the publishing rules see it, with its page counted up."""
        if kind == PROPERTY:
            images = await self._count(PropertyImage.accommodation_id == row.id, PropertyImage)
            rooms = await self._count(
                (RoomType.accommodation_id == row.id) & RoomType.is_active.is_(True),
                RoomType,
            )
            return Candidate(
                name=row.name,
                is_active=row.is_active,
                # The same paragraph the proposal would print, approved copy
                # first (§4.4). A page is refused for having none of the three.
                copy=await property_copy(self.db, row),
                images=images,
                has_location=row.latitude is not None and row.longitude is not None,
                room_types=rooms,
            )
        if kind == DESTINATION:
            images = await self._count(
                DestinationImage.destination_id == row.id, DestinationImage
            )
            return Candidate(
                name=row.name,
                is_active=row.is_active,
                copy=row.description,
                images=images,
                has_location=row.latitude is not None and row.longitude is not None,
            )
        # An activity has no images of its own in this schema and no
        # coordinates; it is shown on the destination's page. Reporting "no
        # image" for every activity forever would be noise, so the counts it
        # cannot have are reported as satisfied rather than missing.
        return Candidate(
            name=row.name,
            is_active=row.is_active,
            copy=row.description,
            images=1,
            has_location=True,
        )

    async def _count(self, where: Any, model: Any) -> int:
        return int(
            (
                await self.db.execute(
                    select(func.count()).select_from(model).where(where)
                )
            ).scalar_one()
        )


class PublicSiteService:
    """What an unauthenticated visitor may read.

    Every query here filters on ``is_published`` **and** ``is_active``. Both,
    not either: a property that was published and has since been deactivated
    cannot be quoted, and a page for something the quote engine will refuse to
    price is a page that generates an apology.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def contact(self) -> ContactRead:
        """How to reach the business, read off the same config the quotation
        document prints (§3.6) rather than typed a second time on the website."""
        config = await DocumentConfigService(self.db).get()
        return ContactRead(
            company_name=config.company_name,
            contact_email=config.contact_email,
            contact_phone=config.contact_phone,
            social_line=config.social_line,
        )

    async def places(self) -> list[Place]:
        rows = await self._live(select(Destination), Destination)
        return [place_of(row) for row in rows]

    async def place(self, slug: str) -> Place:
        row = await self._one(Destination, slug)
        images = await self._images(
            DestinationImage, DestinationImage.destination_id == row.id, "is_cover"
        )
        stays = list(
            (
                await self.db.execute(
                    select(Accommodation.name)
                    .where(
                        Accommodation.destination_id == row.id,
                        Accommodation.is_published.is_(True),
                        Accommodation.is_active.is_(True),
                    )
                    .order_by(Accommodation.name)
                )
            )
            .scalars()
            .all()
        )
        doing = list(
            (
                await self.db.execute(
                    select(Activity.name)
                    .where(
                        Activity.destination_id == row.id,
                        Activity.is_published.is_(True),
                        Activity.is_active.is_(True),
                    )
                    .order_by(Activity.name)
                )
            )
            .scalars()
            .all()
        )
        return place_of(row, images=images, stays=stays, activities=doing)

    async def properties(self, *, destination: str | None = None) -> list[Property]:
        stmt = select(Accommodation)
        if destination:
            place = await self._one(Destination, destination)
            stmt = stmt.where(Accommodation.destination_id == place.id)
        rows = await self._live(stmt, Accommodation)
        places = await self._place_names([row.destination_id for row in rows])
        out: list[Property] = []
        for row in rows:
            name, slug = places.get(row.destination_id, ("", ""))
            out.append(
                property_of(
                    row,
                    copy=await property_copy(self.db, row),
                    destination=name,
                    destination_slug=slug,
                )
            )
        return out

    async def property_page(self, slug: str) -> Property:
        row = await self._one(Accommodation, slug)
        images = await self._images(
            PropertyImage, PropertyImage.accommodation_id == row.id, "is_hero"
        )
        places = await self._place_names([row.destination_id])
        name, place_slug = places.get(row.destination_id, ("", ""))
        rooms = [
            f"{one.name} (sleeps {one.max_occupancy})"
            for one in sorted(row.room_types, key=lambda one: one.name)
            if one.is_active
        ]
        return property_of(
            row,
            copy=await property_copy(self.db, row),
            destination=name,
            destination_slug=place_slug,
            rooms=rooms,
            images=images,
        )

    async def experiences(
        self, *, destination: str | None = None
    ) -> list[Experience]:
        stmt = select(Activity)
        if destination:
            place = await self._one(Destination, destination)
            stmt = stmt.where(Activity.destination_id == place.id)
        rows = await self._live(stmt, Activity)
        places = await self._place_names(
            [row.destination_id for row in rows if row.destination_id]
        )
        out: list[Experience] = []
        for row in rows:
            name, slug = places.get(row.destination_id, ("", ""))
            out.append(experience_of(row, destination=name, destination_slug=slug))
        return out

    async def image(self, kind: str, image_id: uuid.UUID) -> Any:
        """One image row, but only if what it belongs to is published.

        The check is the point. Without it the image endpoint would be an
        unauthenticated read of every photograph in the system, including the
        ones on a property nobody has decided to advertise — and an id is not
        a secret.
        """
        image: Any
        parent: Any
        if kind == PROPERTY:
            image = await self.db.get(PropertyImage, image_id)
            parent = (
                await self.db.get(Accommodation, image.accommodation_id)
                if image is not None
                else None
            )
        elif kind == DESTINATION:
            image = await self.db.get(DestinationImage, image_id)
            parent = (
                await self.db.get(Destination, image.destination_id)
                if image is not None
                else None
            )
        else:
            raise NotFoundError("No such image.")

        if (
            image is None
            or parent is None
            or not parent.is_published
            or not parent.is_active
        ):
            # The same answer as a missing image, deliberately: distinguishing
            # them tells a stranger which ids exist.
            raise NotFoundError("No such image.")
        return image

    # -- internals ---------------------------------------------------------- #

    async def _live(self, stmt: Select[Any], model: Any) -> list[Any]:
        stmt = stmt.where(
            model.is_published.is_(True), model.is_active.is_(True)
        ).order_by(model.name)
        return list((await self.db.execute(stmt)).scalars().all())

    async def _one(self, model: Any, slug: str) -> Any:
        row = (
            await self.db.execute(
                select(model).where(
                    model.slug == slug,
                    model.is_published.is_(True),
                    model.is_active.is_(True),
                )
            )
        ).scalar_one_or_none()
        if row is None:
            raise NotFoundError("There is no page here.")
        return row

    async def _place_names(
        self, ids: list[uuid.UUID | None]
    ) -> dict[uuid.UUID, tuple[str, str]]:
        wanted = {one for one in ids if one is not None}
        if not wanted:
            return {}
        rows = (
            await self.db.execute(
                select(Destination.id, Destination.name, Destination.slug).where(
                    Destination.id.in_(wanted)
                )
            )
        ).all()
        return {row[0]: (row[1], row[2]) for row in rows}

    async def _images(self, model: Any, where: Any, lead_flag: str) -> list[Image]:
        rows = list(
            (
                await self.db.execute(
                    select(model).where(where).order_by(model.sort_order, model.id)
                )
            )
            .scalars()
            .all()
        )
        kind = PROPERTY if model is PropertyImage else DESTINATION
        return [
            Image(
                id=str(row.id),
                url=f"/api/v1/public/images/{kind}/{row.id}",
                alt_text=row.alt_text,
                width=row.width,
                height=row.height,
                is_lead=bool(getattr(row, lead_flag, False)),
            )
            for row in rows
        ]


class EnquiryService:
    """An enquiry off the website becomes a lead and a logged conversation.

    Deliberately **not** its own table. An enquiry is a lead at the stage new
    ones arrive at (§5.2) and an inbound entry in the contact log (§5.3), and
    both of those already exist with a morning list, a pipeline report and a
    first-response measurement built on them. A parallel ``enquiries`` table
    would be a second inbox that nobody opens, and the leads it duplicated
    would be the ones that never got answered.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def capture(
        self, form: Submitted, *, today: date | None = None
    ) -> Lead | None:
        """Record a website enquiry. ``None`` means it was dropped as spam.

        The caller answers the same way either way — see
        :func:`app.modules.public.enquiry.check_enquiry` on the trap field.
        """
        try:
            accepted = check_enquiry(form, today=today or date.today())
        except EnquiryRefused as exc:
            # The message is the one the rules wrote: it is the last thing this
            # business says to whoever filled the form, and a generic
            # "validation failed" would be the worst possible version of it.
            raise AppError(exc.message) from exc
        if accepted.discard:
            logger.info("Dropped an enquiry that filled the trap field.")
            return None

        lead = await LeadService(self.db).create(
            contact_name=accepted.name,
            contact_email=accepted.email,
            contact_phone=accepted.phone,
            source="website",
            # The page is the "detail" half of the pair §5.2 wanted: a source
            # of "website" alone answers a marketing question with "the
            # internet".
            source_detail=accepted.page,
            destination_interest=accepted.destination,
            travel_from=accepted.travel_from,
            travel_to=accepted.travel_to,
            pax_estimate=accepted.pax,
            # No owner and no stage: a stranger's form does not get to choose
            # whose name is on the deal or how far along it is. It arrives
            # where new enquiries arrive and somebody picks it up.
            today=today,
        )

        # The client's own words, in the log, stamped inbound. This is what
        # makes the enquiry measurable: §5.3's first-response clock starts
        # here, and until now it could only start from a human remembering to
        # log something.
        await CommsService(self.db).log(
            subject=LEAD,
            subject_id=lead.id,
            channel="website",
            direction=INBOUND,
            subject_line="Website enquiry",
            body=as_log_entry(accepted),
            reached=True,
            actor_id=None,
        )
        return await LeadService(self.db).get(lead.id)


class EstimateService:
    """An indicative price for a trip a stranger is still imagining (§6.3).

    Reuses the real build-up arithmetic (:mod:`app.modules.quotes.options`)
    against real, published, currently-active rates. See
    :mod:`app.modules.public.estimate` for exactly what is simplified and why
    — one snapshot date rather than a stay, one representative property per
    tier, a child priced as an adult, nothing for transfers or park fees.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def price_trip(
        self,
        legs: list[tuple[str, str, int]],
        *,
        resident: bool,
        adults: int,
        children: int,
        today: date | None = None,
    ) -> tuple[list[LegPriced], Combined]:
        """``legs`` is ``(destination_slug, tier, nights)``.

        A child is priced as an adult (see the module docstring on why that is
        the honest default rather than an invented discount), so the pax used
        for every leg's room-plan and build-up is simply ``adults + children``.
        """
        when = today or date.today()
        pax = max(adults, 1) + max(children, 0)
        key = "resident" if resident else "non_resident"
        residences = await residence_ids(self.db, [key])
        residence_id = residences[key]
        config = await PricingConfigService(self.db).get()

        priced = [
            await self._price_leg(
                slug, tier, nights, pax=pax, residence_id=residence_id,
                config=config, today=when,
            )
            for slug, tier, nights in legs
        ]
        return priced, combine(priced)

    async def _price_leg(
        self,
        slug: str,
        tier: str,
        nights: int,
        *,
        pax: int,
        residence_id: uuid.UUID,
        config: Any,
        today: date,
    ) -> LegPriced:
        try:
            lo, hi = star_band(tier)
        except EstimateRefused as exc:
            return LegPriced(
                destination=slug, tier=tier, nights=nights, refused=exc
            )

        place = (
            await self.db.execute(
                select(Destination).where(Destination.slug == slug)
            )
        ).scalar_one_or_none()
        if place is None:
            return LegPriced(
                destination=slug,
                tier=tier,
                nights=nights,
                refused=EstimateRefused(
                    NO_PROPERTY, f"'{slug}' is not one of our destinations."
                ),
            )

        # Every active rate, for every published+active property of this
        # destination and tier, at every occupancy and meal plan — one query,
        # narrowed in Python exactly as the real engine narrows a property's
        # rates (app.modules.quotes.option_pricing._rates), simplified to a
        # single day because the builder collects no travel dates.
        rows = (
            await self.db.execute(
                select(
                    Accommodation.id,
                    Accommodation.name,
                    RoomType.id,
                    RoomType.name,
                    MealPlan.code,
                    AccommodationRate.occupancy,
                    AccommodationRate.rate_per_night,
                    AccommodationRate.currency,
                )
                .select_from(AccommodationRate)
                .join(RoomType, RoomType.id == AccommodationRate.room_type_id)
                .join(MealPlan, MealPlan.id == AccommodationRate.meal_plan_id)
                .join(Accommodation, Accommodation.id == RoomType.accommodation_id)
                .where(
                    Accommodation.destination_id == place.id,
                    Accommodation.is_published.is_(True),
                    Accommodation.is_active.is_(True),
                    Accommodation.star_rating.between(lo, hi),
                    RoomType.is_active.is_(True),
                    AccommodationRate.residence_category_id == residence_id,
                    AccommodationRate.is_active.is_(True),
                    AccommodationRate.effective_from <= today,
                    AccommodationRate.effective_to >= today,
                )
            )
        ).all()

        if not rows:
            return LegPriced(
                destination=place.name,
                tier=tier,
                nights=nights,
                refused=EstimateRefused(
                    NO_PROPERTY,
                    f"We do not yet have a published {tier} property in "
                    f"{place.name} with a current rate. A consultant can still "
                    f"put figures to this.",
                ),
            )

        # Index by (accommodation, room type), find the cheapest one that can
        # actually answer a BB request (the fallback chain §3.4 already
        # defines), then price the whole party against it.
        groups: dict[tuple[uuid.UUID, uuid.UUID], dict[str, Any]] = {}
        for acc_id, acc_name, rt_id, rt_name, code, occupancy, rate, currency in rows:
            group = groups.setdefault(
                (acc_id, rt_id),
                {"name": acc_name, "room": rt_name, "codes": set(), "rates": {}},
            )
            group["codes"].add(code.upper())
            # Keyed by (plan, occupancy) rather than occupancy alone: the same
            # room-night published in more than one currency is exactly the
            # §3.12 collision, and here it simply means two rate rows to weigh
            # rather than one — the cheaper of the two wins on its own merits
            # once priced, same as everywhere else.
            group["rates"].setdefault(code.upper(), {})[occupancy] = (
                rate,
                currency,
            )

        best: tuple[Decimal, str, str, dict[str, Any]] | None = None
        for group in groups.values():
            plan, _ = resolve_meal_plan("BB", group["codes"])
            if plan is None:
                continue
            occupancy_rates = group["rates"][plan]
            by_occupancy = {occ: rate for occ, (rate, _c) in occupancy_rates.items()}
            total = price_rooms(by_occupancy, pax=pax)
            if total is None:
                continue
            # Every room in the plan must be filed in the same currency. A
            # property publishing one occupancy in KES and another in USD is
            # the §3.12 collision in a form nothing downstream can safely sum
            # — refused for this candidate rather than silently mixed.
            used: set[int] = set()
            for headcount in room_plan(pax, ROOM_CAPACITY):
                found = rate_for_occupancy(by_occupancy, headcount)
                assert found is not None  # price_rooms already confirmed this
                used.add(found[0])
            currencies = {occupancy_rates[occ][1] for occ in used}
            if len(currencies) != 1:
                continue
            currency = currencies.pop()
            if best is None or total < best[0]:
                best = (total, plan, currency, group)

        if best is None:
            return LegPriced(
                destination=place.name,
                tier=tier,
                nights=nights,
                refused=EstimateRefused(
                    NO_RATE,
                    f"{place.name} has a {tier} property on file, but nothing "
                    f"priced for a group of {pax} on a bed-and-breakfast basis "
                    f"or better right now. A consultant can confirm a rate "
                    f"directly.",
                ),
            )

        per_night, meal_plan, currency, group = best

        built = build_up(
            components={"accommodation": per_night * nights},
            pax=pax,
            contingency_pct=config.contingency_pct,
            profit_pct=config.profit_pct,
            rounding_step=config.per_person_rounding_by_currency.get(
                currency, config.per_person_rounding
            ),
            uniform_group=True,
        )
        return LegPriced(
            destination=place.name,
            tier=tier,
            nights=nights,
            property_name=group["name"],
            room_type=group["room"],
            meal_plan=meal_plan,
            currency=currency,
            per_person=built.per_person,
            group_total=built.group_total,
        )


def refuse_unknown_kind(kind: str) -> None:
    """Shared by the routers, so 'kind' means one thing in one place."""
    if (kind or "").strip().lower() not in _MODELS:
        raise AppError(f"'{kind}' is not something with a public page.")


__all__ = [
    "ACTIVITY",
    "DESTINATION",
    "PROPERTY",
    "EnquiryService",
    "EstimateService",
    "PublicSiteService",
    "PublishService",
]
