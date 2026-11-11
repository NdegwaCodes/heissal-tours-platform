"""What the world may see of the catalogue. Pure functions (§6.1).

Two jobs, and the first one is the reason this module exists at all.

**Sellable is not publishable.** Every catalogue row already carries
``is_active``, and it has meant one thing since §2: this may be used in a
quote. It is set by whoever loads a rate sheet. It is *not* a decision about a
website, and if the public site read it there would be no way to contract with
a property and not advertise it — a rate-sheet import would publish forty
hotels, and the first anybody would know is a client ringing about one the
business does not want to sell. So publishing is its own column, its own
permission and its own act, with a person's name and a timestamp on it.

**The public view is built from an allow-list**, for §7.2's reason and with
the same failure mode in mind. A catalogue row carries ``supplier_id``, and
whose contract sits behind a lodge is commercial intelligence a competitor
would read off the website in an afternoon. A page assembled by removing keys
is one forgotten key away from publishing it, and the key that gets forgotten
is always the one added later by somebody working on rates who has never read
this file. So nothing is removed: named fields are copied across, and a column
the table gains tomorrow does not appear on the internet until somebody adds
it here on purpose.

Nothing here prices anything. The public surface carries no rate, no cost, no
margin and no "from" figure: a price on a website is a promise, and every
figure this system produces depends on dates, party shape, residence category
and season (§2.3). "From KES 45,000" with none of those attached is a number
the business would then have to honour or explain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# --------------------------------------------------------------------------- #
# Publishing
# --------------------------------------------------------------------------- #

#: Cannot be published because it cannot be sold.
INACTIVE = "publish_inactive"
#: Cannot be published because there is nothing to say about it.
NO_COPY = "publish_no_copy"

#: Will publish, but the page will be thin. Reported, not refused — see
#: :func:`check_page`.
NO_IMAGE = "page_no_image"
NO_LOCATION = "page_no_location"
NO_ROOMS = "page_no_room_types"


class PublishRefused(Exception):
    """Publishing this would put a broken page on the internet."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Candidate:
    """A catalogue row as the publishing rules see it. Not the ORM row."""

    name: str
    is_active: bool = True
    #: The client-facing paragraph. For a property this is ``blurb``, the copy
    #: §3 already writes into proposals — not ``description``, which is the
    #: internal note an agent keeps.
    copy: str | None = None
    images: int = 0
    has_location: bool = False
    room_types: int = 0


def check_publish(candidate: Candidate) -> None:
    """Whether this row may go on the website.

    Two refusals only, and both are about the page being broken rather than
    about it being good. Judging whether copy is any *good* is not something
    this can do, and a rule that tried would be a rule somebody works around.
    """
    if not candidate.is_active:
        raise PublishRefused(
            INACTIVE,
            f"{candidate.name} is not active, so it cannot be sold — and "
            f"advertising something the quote engine will refuse to price is "
            f"worse than not advertising it. Reactivate it first.",
        )
    if not (candidate.copy or "").strip():
        raise PublishRefused(
            NO_COPY,
            f"{candidate.name} has no description, so its page would be a name "
            f"and a photograph. Write the copy first — it is the same "
            f"paragraph the proposals use.",
        )


@dataclass(frozen=True)
class Concern:
    """Something thin about a page. Not a refusal."""

    code: str
    message: str


def check_page(candidate: Candidate, *, wants_rooms: bool = False) -> list[Concern]:
    """What will look thin once this is live.

    Reported rather than enforced, as everywhere else in this system: a
    property with no photograph yet is a real thing to publish the week the
    photographer is booked, and a rule that blocked it would be worked around
    by publishing something worse.
    """
    found: list[Concern] = []
    if candidate.images == 0:
        found.append(
            Concern(
                NO_IMAGE,
                f"{candidate.name} has no images, so its page will be text on "
                f"a white background. Nobody books that.",
            )
        )
    if not candidate.has_location:
        found.append(
            Concern(
                NO_LOCATION,
                f"{candidate.name} has no coordinates, so it cannot go on a map.",
            )
        )
    if wants_rooms and candidate.room_types == 0:
        found.append(
            Concern(
                NO_ROOMS,
                f"{candidate.name} has no room types, so the page cannot say "
                f"what you would be staying in.",
            )
        )
    return found


# --------------------------------------------------------------------------- #
# The allow-list
# --------------------------------------------------------------------------- #

#: A destination's public fields. ``description`` is the public paragraph here
#: — unlike a property, a destination has no separate proposal blurb.
_PLACE_FIELDS = (
    "name",
    "slug",
    "type",
    "country",
    "region",
    "latitude",
    "longitude",
    "description",
)

#: A property's public fields.
#:
#: Named absences, so that nobody has to wonder whether they were forgotten:
#:
#: * ``supplier_id`` — whose contract sits behind a lodge is commercial
#:   intelligence, and a competitor would read the business's supplier list off
#:   the website in an afternoon.
#: * ``description`` — not because it is secret (§3's proposals fall back to
#:   it), but because the paragraph a page shows is *resolved* rather than
#:   read off one column: approved copy, then ``blurb``, then ``description``.
#:   See ``narratives.service.property_copy``, and ``description`` below.
#: * ``website`` — sending somebody to the property's own booking page loses
#:   the sale that paid for the page they are reading. This one is a commercial
#:   call rather than a safety one, and the client's to overturn.
#: * every rate, supplement, discount and VAT field. See the module docstring
#:   on why there is no "from" price either.
_PROPERTY_FIELDS = (
    "name",
    "slug",
    "category",
    "star_rating",
    "latitude",
    "longitude",
    "check_in_time",
    "check_out_time",
)

_ACTIVITY_FIELDS = (
    "name",
    "slug",
    "description",
    "duration_minutes",
)


@dataclass(frozen=True)
class Image:
    """One photograph, as a visitor sees it: a URL, a size and its alt text."""

    id: str
    url: str
    alt_text: str | None = None
    width: int | None = None
    height: int | None = None
    is_lead: bool = False


@dataclass(frozen=True)
class Place:
    """A destination page."""

    name: str = ""
    slug: str = ""
    type: str = ""
    country: str = ""
    region: str | None = None
    latitude: Any = None
    longitude: Any = None
    description: str | None = None
    images: list[Image] = field(default_factory=list)
    #: Properties and activities published *here*, named only.
    stays: list[str] = field(default_factory=list)
    activities: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Property:
    """A property page."""

    name: str = ""
    slug: str = ""
    category: str = ""
    star_rating: int | None = None
    latitude: Any = None
    longitude: Any = None
    check_in_time: str | None = None
    check_out_time: str | None = None
    #: The resolved paragraph — approved copy first. Supplied by the caller
    #: rather than copied off a column, because the precedence is shared with
    #: the proposal (§4.4) and the two must not drift.
    description: str | None = None
    destination: str = ""
    destination_slug: str = ""
    #: Room names and how many they sleep. No rate, and no availability: this
    #: system has never modelled availability, and a website that implied it
    #: had would be lying in the most expensive way available.
    rooms: list[str] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)


@dataclass(frozen=True)
class Experience:
    """An activity, as a page or a list entry."""

    name: str = ""
    slug: str = ""
    description: str | None = None
    duration_minutes: int | None = None
    destination: str = ""
    destination_slug: str = ""


def _copy(row: Any, names: tuple[str, ...]) -> dict[str, Any]:
    """Named fields only. The whole point of this module — see the docstring."""
    return {name: getattr(row, name, None) for name in names}


def place_of(
    row: Any,
    *,
    images: list[Image] | None = None,
    stays: list[str] | None = None,
    activities: list[str] | None = None,
) -> Place:
    data = _copy(row, _PLACE_FIELDS)
    return Place(
        name=data["name"] or "",
        slug=data["slug"] or "",
        type=data["type"] or "",
        country=data["country"] or "",
        region=data["region"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        description=data["description"],
        images=images or [],
        stays=stays or [],
        activities=activities or [],
    )


def property_of(
    row: Any,
    *,
    copy: str | None = None,
    destination: str = "",
    destination_slug: str = "",
    rooms: list[str] | None = None,
    images: list[Image] | None = None,
) -> Property:
    data = _copy(row, _PROPERTY_FIELDS)
    return Property(
        name=data["name"] or "",
        slug=data["slug"] or "",
        category=data["category"] or "",
        star_rating=data["star_rating"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        check_in_time=data["check_in_time"],
        check_out_time=data["check_out_time"],
        # Passed in rather than read off the row: see Property.description.
        # The fallback keeps this usable from a test or a list view that has
        # not resolved the approved copy.
        description=copy if copy is not None else getattr(row, "blurb", None),
        destination=destination,
        destination_slug=destination_slug,
        rooms=rooms or [],
        images=images or [],
    )


def experience_of(
    row: Any, *, destination: str = "", destination_slug: str = ""
) -> Experience:
    data = _copy(row, _ACTIVITY_FIELDS)
    return Experience(
        name=data["name"] or "",
        slug=data["slug"] or "",
        description=data["description"],
        duration_minutes=data["duration_minutes"],
        destination=destination,
        destination_slug=destination_slug,
    )


__all__ = [
    "INACTIVE",
    "NO_COPY",
    "NO_IMAGE",
    "NO_LOCATION",
    "NO_ROOMS",
    "Candidate",
    "Concern",
    "Experience",
    "Image",
    "Place",
    "Property",
    "PublishRefused",
    "check_page",
    "check_publish",
    "experience_of",
    "place_of",
    "property_of",
]
