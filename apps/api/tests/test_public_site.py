"""What the world may see, and what an enquiry may be. Pure rules (§6.1).

Figures and properties are invented, as everywhere in this suite. No supplier
contract rate appears in this repository.

The failure these rules exist to prevent is a quiet one: a rate-sheet import
that publishes forty hotels, or a column added to the catalogue next month
that turns up on the internet because a response model was built from the ORM
row.
"""

from __future__ import annotations

from datetime import date

import pytest

from app.modules.public.enquiry import (
    BAD_EMAIL,
    BAD_PAX,
    BAD_WINDOW,
    MAX_MESSAGE,
    NO_NAME,
    NO_REPLY_TO,
    TOO_LONG,
    EnquiryRefused,
    Submitted,
    as_log_entry,
    check_enquiry,
)
from app.modules.public.site import (
    INACTIVE,
    NO_COPY,
    NO_IMAGE,
    NO_LOCATION,
    NO_ROOMS,
    Candidate,
    PublishRefused,
    check_page,
    check_publish,
    place_of,
    property_of,
)

TODAY = date(2026, 9, 6)


class _Row:
    """Stands in for an ORM row. Deliberately carries more than it should."""

    def __init__(self, **fields):
        for key, value in fields.items():
            setattr(self, key, value)


# --------------------------------------------------------------------------- #
# Sellable is not publishable
# --------------------------------------------------------------------------- #


def _candidate(**over):
    fields = {
        "name": "Reef House",
        "is_active": True,
        "copy": "A small property on the south coast.",
        "images": 4,
        "has_location": True,
        "room_types": 3,
    }
    fields.update(over)
    return Candidate(**fields)


def test_something_we_cannot_sell_cannot_be_advertised():
    with pytest.raises(PublishRefused) as raised:
        check_publish(_candidate(is_active=False))
    assert raised.value.code == INACTIVE
    assert "the quote engine will refuse to price" in raised.value.message


def test_a_page_with_no_copy_is_refused():
    """A name and a photograph is not a page."""
    with pytest.raises(PublishRefused) as raised:
        check_publish(_candidate(copy="   "))
    assert raised.value.code == NO_COPY
    assert "the same paragraph the proposals use" in raised.value.message


def test_a_property_with_copy_and_a_contract_publishes():
    check_publish(_candidate())


def test_a_thin_page_is_reported_and_not_refused():
    """A property whose photographs arrive on Thursday publishes on Wednesday.

    A rule that blocked it would be worked around by publishing something
    worse, which is the whole argument for reporting rather than concluding.
    """
    check_publish(_candidate(images=0))
    found = check_page(_candidate(images=0))
    assert [one.code for one in found] == [NO_IMAGE]
    assert "Nobody books that" in found[0].message


def test_a_property_with_no_rooms_cannot_say_what_you_sleep_in():
    found = check_page(_candidate(room_types=0), wants_rooms=True)
    assert [one.code for one in found] == [NO_ROOMS]


def test_room_types_are_only_asked_of_a_property():
    """A destination has no rooms, and reporting that forever would be noise."""
    assert check_page(_candidate(room_types=0)) == []


def test_no_coordinates_means_no_map():
    found = check_page(_candidate(has_location=False))
    assert [one.code for one in found] == [NO_LOCATION]


def test_a_complete_page_has_nothing_to_report():
    assert check_page(_candidate(), wants_rooms=True) == []


# --------------------------------------------------------------------------- #
# The allow-list
# --------------------------------------------------------------------------- #


def test_a_property_page_never_carries_the_supplier():
    """The failure this module exists for.

    Whose contract sits behind a lodge is commercial intelligence, and a
    competitor would read the business's whole supplier list off the website
    in an afternoon.
    """
    page = property_of(
        _Row(
            name="Reef House",
            slug="reef-house",
            category="lodge",
            star_rating=4,
            latitude=None,
            longitude=None,
            check_in_time="14:00",
            check_out_time="10:00",
            blurb="A small property on the south coast.",
            # None of the following may appear on a page.
            supplier_id="3f0c-not-a-real-id",
            description="Owner is difficult about children. Chase the 2027 contract.",
            website="https://example.invalid",
            is_active=True,
        )
    )
    assert page.name == "Reef House"
    assert page.description == "A small property on the south coast."
    fields = vars(page)
    assert "supplier_id" not in fields
    assert "website" not in fields
    assert "Owner is difficult" not in str(fields)


def test_a_column_added_tomorrow_does_not_appear_today():
    """The point of copying named fields instead of removing keys.

    A future migration adds ``margin_override`` to the catalogue. Nobody
    touches this module. It must not reach the internet.
    """
    page = property_of(
        _Row(
            name="Reef House",
            slug="reef-house",
            category="lodge",
            star_rating=None,
            latitude=None,
            longitude=None,
            check_in_time=None,
            check_out_time=None,
            blurb="Copy.",
            margin_override="0.42",
        )
    )
    assert "margin_override" not in str(vars(page))


def test_a_destination_page_uses_its_own_description():
    page = place_of(
        _Row(
            name="Diani",
            slug="diani",
            type="beach",
            country="Kenya",
            region="Coast",
            latitude=None,
            longitude=None,
            description="White sand and a reef.",
        ),
        stays=["Reef House"],
        activities=["Wasini day trip"],
    )
    assert page.description == "White sand and a reef."
    assert page.stays == ["Reef House"]
    assert page.activities == ["Wasini day trip"]


def test_a_page_carries_no_price_of_any_kind():
    """No rate, no cost, no "from" figure — see the module docstring.

    Every figure this system produces depends on dates, party shape,
    residence category and season. "From KES 45,000" with none of those
    attached is a number the business would have to honour or explain.
    """
    page = property_of(
        _Row(
            name="Reef House",
            slug="reef-house",
            category="lodge",
            star_rating=None,
            latitude=None,
            longitude=None,
            check_in_time=None,
            check_out_time=None,
            blurb="Copy.",
            rate_per_night="18500",
            currency="KES",
        )
    )
    text = str(vars(page))
    assert "18500" not in text
    assert "rate_per_night" not in text


# --------------------------------------------------------------------------- #
# An enquiry off the website
# --------------------------------------------------------------------------- #


def _form(**over):
    fields = {
        "name": "  Amina Yusuf ",
        "email": "amina@example.test",
        "phone": None,
        "destination": "Diani",
        "travel_from": date(2026, 12, 20),
        "travel_to": date(2026, 12, 27),
        "pax": 4,
        "message": "Two adults and two children, somewhere on the beach.",
        "page": "/destinations/diani",
    }
    fields.update(over)
    return Submitted(**fields)


def test_a_name_is_required_because_dear_customer_is_how_a_chain_writes():
    with pytest.raises(EnquiryRefused) as raised:
        check_enquiry(_form(name="  "), today=TODAY)
    assert raised.value.code == NO_NAME


def test_either_an_email_or_a_telephone_number_but_not_both():
    """Half of this market types a phone number and nothing else."""
    with pytest.raises(EnquiryRefused) as raised:
        check_enquiry(_form(email=None, phone=None), today=TODAY)
    assert raised.value.code == NO_REPLY_TO
    assert "no way to answer you" in raised.value.message

    only_phone = check_enquiry(_form(email=None, phone="+254 700 000 000"), today=TODAY)
    assert only_phone.phone == "+254 700 000 000"
    assert only_phone.email is None


def test_a_telephone_number_in_the_email_box_is_caught():
    with pytest.raises(EnquiryRefused) as raised:
        check_enquiry(_form(email="0700000000"), today=TODAY)
    assert raised.value.code == BAD_EMAIL


def test_dates_the_wrong_way_round_are_refused():
    with pytest.raises(EnquiryRefused) as raised:
        check_enquiry(
            _form(travel_from=date(2026, 12, 27), travel_to=date(2026, 12, 20)),
            today=TODAY,
        )
    assert raised.value.code == BAD_WINDOW
    assert "the wrong way round" in raised.value.message


def test_a_travel_date_already_past_is_flagged_and_not_refused():
    """Almost always a date picker left on last month.

    Refusing it throws away a real enquiry over a correction an agent makes in
    two seconds on the telephone.
    """
    got = check_enquiry(_form(travel_from=date(2026, 8, 1), travel_to=None), today=TODAY)
    assert got.travel_from == date(2026, 8, 1)
    assert any("already passed" in note for note in got.notes)


def test_no_dates_at_all_is_the_most_valuable_kind_of_enquiry():
    """"Sometime in August, probably" is a real enquiry."""
    got = check_enquiry(_form(travel_from=None, travel_to=None, pax=None), today=TODAY)
    assert got.travel_from is None
    assert got.pax is None


def test_a_name_and_a_number_and_nothing_else_is_a_perfectly_good_ring_me():
    got = check_enquiry(
        Submitted(name="Mr Otieno", phone="+254 700 000 000"), today=TODAY
    )
    assert got.message == ""
    assert any("No message" in note for note in got.notes)


def test_a_pasted_novel_is_refused_with_the_limit_stated():
    with pytest.raises(EnquiryRefused) as raised:
        check_enquiry(_form(message="x" * (MAX_MESSAGE + 1)), today=TODAY)
    assert raised.value.code == TOO_LONG
    assert str(MAX_MESSAGE) in raised.value.message


def test_a_broken_party_size_is_refused_but_a_conference_is_not():
    with pytest.raises(EnquiryRefused) as raised:
        check_enquiry(_form(pax=0), today=TODAY)
    assert raised.value.code == BAD_PAX
    assert check_enquiry(_form(pax=500), today=TODAY).pax == 500


def test_the_name_is_trimmed_and_the_form_is_normalised():
    got = check_enquiry(_form(), today=TODAY)
    assert got.name == "Amina Yusuf"
    assert got.page == "/destinations/diani"


def test_a_filled_trap_is_answered_rather_than_refused():
    """Telling a bot which field to leave alone next time teaches it.

    The caller returns the same 202 a real enquiry gets and drops this one.
    """
    got = check_enquiry(_form(trap="http://spam.invalid"), today=TODAY)
    assert got.discard is True
    assert got.name == ""


def test_the_log_entry_leads_with_the_clients_own_words():
    """An agent reads the sentence the customer typed before anything else."""
    body = as_log_entry(check_enquiry(_form(), today=TODAY))
    assert body.startswith("Two adults and two children")
    assert "Interested in: Diani" in body
    assert "Travel: 20 Dec 2026 to 27 Dec 2026" in body
    assert "Travellers: 4" in body
    assert "Enquired from: /destinations/diani" in body


def test_there_is_no_budget_field():
    """A figure with no currency beside it is not money (CLAUDE.md).

    Guessing shillings because the site is Kenyan reads a European family's
    8,000 as eight thousand shillings.
    """
    assert not hasattr(Submitted(name="x"), "budget")
    assert not hasattr(check_enquiry(_form(), today=TODAY), "budget")
