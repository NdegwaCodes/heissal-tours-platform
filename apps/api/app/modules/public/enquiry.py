"""An enquiry off the website, before it touches the database. Pure (§6.1).

This is the first thing in the platform a stranger can write to, and that
changes what validation is for. Everywhere else a refusal protects the data
from a mistake by somebody who can be asked about it. Here a refusal is a lost
customer: whoever filled the form is not coming back to try again, and the
message they get is the last thing they will read from this business.

So the rules are as few as they can be, and each one is about the enquiry
being *answerable*:

* something to call them by, because "Dear customer" is how a chain hotel
  writes;
* a way to answer — an email address or a telephone number. Not both: half of
  this market types a phone number and nothing else, and demanding an email
  address from them loses the enquiry;
* a travel window that is the right way round;
* a message that fits in a field.

And nothing else. No mandatory dates, because "sometime in August, probably" is
a real enquiry and the most valuable kind. No mandatory party size. No account.

**No budget field.** A figure typed into a website with no currency beside it
is not money (CLAUDE.md), and guessing that a Kenyan site means shillings is
the guess that reads a European family's 8,000 as eight thousand shillings and
sends them a matatu. If the client wants to ask about budget it needs its own
currency selector, which is a conversation about the form and not a default.

**Nothing here decides anything.** A submitted enquiry becomes a lead at the
stage new ones arrive at, with the source ``website``, no owner and no value.
Scoring a stranger's enquiry from the words in it — "honeymoon" is worth more
than "quote please" — is the kind of cleverness that quietly buries the one
that was worth forty thousand dollars.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

#: Long enough for somebody to describe a family trip properly; short enough
#: that a paste of a novel is refused rather than stored.
MAX_MESSAGE = 4000
MAX_NAME = 200
MAX_EMAIL = 255
MAX_PHONE = 50
MAX_DESTINATION = 200
#: A group of five hundred is a real conference enquiry in this market. Ten
#: thousand is a broken form or somebody testing.
MAX_PAX = 10_000

NO_NAME = "enquiry_no_name"
NO_REPLY_TO = "enquiry_no_contact"
BAD_EMAIL = "enquiry_bad_email"
BAD_WINDOW = "enquiry_bad_dates"
BAD_PAX = "enquiry_bad_pax"
TOO_LONG = "enquiry_too_long"

#: Deliberately loose. A validator strict enough to be interesting rejects
#: real addresses — apostrophes, new top-level domains, long subdomains — and
#: the only test that matters is whether a reply arrives, which nothing here
#: can know. This catches a telephone number typed into the email box.
_EMAIL = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")


class EnquiryRefused(Exception):
    """The form cannot be answered as filled in, with something to fix."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Submitted:
    """Exactly what arrived, untrusted and unnormalised."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    destination: str | None = None
    travel_from: date | None = None
    travel_to: date | None = None
    pax: int | None = None
    message: str | None = None
    #: Which page it came from — "/destinations/diani", a campaign landing
    #: page. It is the (source, detail) pair §5.2 said a marketing-spend
    #: question actually needs; a source of "website" alone says only "the
    #: internet".
    page: str | None = None
    #: A field a human never sees and never fills. See :func:`check_enquiry`.
    trap: str | None = None


@dataclass(frozen=True)
class Accepted:
    """A normalised enquiry, ready to become a lead."""

    name: str
    email: str | None
    phone: str | None
    destination: str | None
    travel_from: date | None
    travel_to: date | None
    pax: int | None
    message: str
    page: str | None
    #: True when the trap was filled. The caller still answers 202 — see
    #: :func:`check_enquiry`.
    discard: bool = False
    #: Things worth an agent's eye that are not worth a refusal.
    notes: tuple[str, ...] = ()


def _clean(value: str | None, limit: int) -> str | None:
    text = (value or "").strip()
    return text[:limit] if text else None


def check_enquiry(form: Submitted, *, today: date) -> Accepted:
    """Normalise a submitted form, or refuse it with something a person can fix.

    The trap field is answered rather than refused. A hidden input that a
    browser never shows is filled in only by something automated, and telling
    it that it failed teaches whoever wrote it which field to leave alone; the
    caller returns the same 202 a real enquiry gets and drops this one. It is
    the one place in this codebase that lies about what it did, and it is worth
    it: the alternative is either a CAPTCHA in front of every enquiry or a
    pipeline full of rubbish.
    """
    if (form.trap or "").strip():
        return Accepted(
            name="",
            email=None,
            phone=None,
            destination=None,
            travel_from=None,
            travel_to=None,
            pax=None,
            message="",
            page=_clean(form.page, 200),
            discard=True,
        )

    name = _clean(form.name, MAX_NAME)
    if not name:
        raise EnquiryRefused(
            NO_NAME, "Please tell us your name so we know who we are writing to."
        )

    email = _clean(form.email, MAX_EMAIL)
    phone = _clean(form.phone, MAX_PHONE)
    if not email and not phone:
        raise EnquiryRefused(
            NO_REPLY_TO,
            "Please leave an email address or a telephone number, otherwise we "
            "have no way to answer you.",
        )
    if email and not _EMAIL.match(email):
        raise EnquiryRefused(
            BAD_EMAIL,
            f"'{email}' does not look like an email address. Check it, or "
            f"leave a telephone number instead.",
        )

    message = (form.message or "").strip()
    if len(message) > MAX_MESSAGE:
        raise EnquiryRefused(
            TOO_LONG,
            f"Your message is longer than we can take ({len(message)} "
            f"characters against a limit of {MAX_MESSAGE}). Send us the outline "
            f"and we will call you.",
        )

    if form.pax is not None and (form.pax < 1 or form.pax > MAX_PAX):
        raise EnquiryRefused(
            BAD_PAX, "Please give the number of travellers as a whole number."
        )

    if form.travel_from and form.travel_to and form.travel_to < form.travel_from:
        raise EnquiryRefused(
            BAD_WINDOW,
            "The return date is before the departure date. Have they been "
            "entered the wrong way round?",
        )

    notes: list[str] = []
    if form.travel_from and form.travel_from < today:
        # Not a refusal. It is almost always a typo or a date picker left on
        # last month, and refusing it throws away a real enquiry over a
        # correction an agent makes in two seconds on the telephone. Flagged so
        # they know to make it.
        notes.append(
            f"Travel date given as {form.travel_from:%d %B %Y}, which has "
            f"already passed — check it when you reply."
        )
    if not message:
        # Also not a refusal: a name, a phone number and nothing else is a
        # perfectly good "ring me", and it is how a lot of this market enquires.
        notes.append("No message was left with the enquiry.")

    return Accepted(
        name=name,
        email=email,
        phone=phone,
        destination=_clean(form.destination, MAX_DESTINATION),
        travel_from=form.travel_from,
        travel_to=form.travel_to,
        pax=form.pax,
        message=message,
        page=_clean(form.page, 200),
        notes=tuple(notes),
    )


def as_log_entry(accepted: Accepted) -> str:
    """The body of the §5.3 entry this enquiry becomes.

    The client's own words, kept verbatim and first. An agent picking this up
    is going to read the sentence the customer typed before anything else, and
    a summary of it in our words is a worse version of the only piece of
    genuine information in the row.
    """
    lines: list[str] = []
    if accepted.message:
        lines.append(accepted.message)
    else:
        lines.append("(No message left.)")
    detail: list[str] = []
    if accepted.destination:
        detail.append(f"Interested in: {accepted.destination}")
    if accepted.travel_from:
        window = f"{accepted.travel_from:%d %b %Y}"
        if accepted.travel_to:
            window += f" to {accepted.travel_to:%d %b %Y}"
        detail.append(f"Travel: {window}")
    if accepted.pax:
        detail.append(f"Travellers: {accepted.pax}")
    if accepted.page:
        detail.append(f"Enquired from: {accepted.page}")
    if detail:
        lines.append("")
        lines.extend(detail)
    if accepted.notes:
        lines.append("")
        lines.extend(accepted.notes)
    return "\n".join(lines)


__all__ = [
    "BAD_EMAIL",
    "BAD_PAX",
    "BAD_WINDOW",
    "MAX_MESSAGE",
    "MAX_PAX",
    "NO_NAME",
    "NO_REPLY_TO",
    "TOO_LONG",
    "Accepted",
    "EnquiryRefused",
    "Submitted",
    "as_log_entry",
    "check_enquiry",
]
