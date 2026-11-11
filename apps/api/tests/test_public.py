"""The public surface, over HTTP (§6.1).

Properties and figures are invented, as everywhere in this suite.

These tests build their own throwaway destination and property rather than
using ``sample_catalogue``: publishing mutates the row, and a shared
read-mostly dataset must not depend on execution order (see conftest).
"""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.modules.comms.models import Communication
from app.modules.leads.models import Lead, LeadStageEvent
from tests.conftest import auth_headers, unique_email

pytestmark = pytest.mark.asyncio(loop_scope="session")

V1 = settings.API_V1_STR


@pytest_asyncio.fixture(loop_scope="session")
async def swept_enquiries():
    """Delete the leads this module's enquiries create.

    Not optional. The suite runs against a database that persists between
    invocations, and a website enquiry nobody answers is — correctly — the top
    item on ``/leads/attention``, so leaving these behind changes what another
    module's tests see. It did: §5.2's "first on the list" test started failing
    for a perfectly good reason.

    Emails are collected rather than ids, because the endpoint deliberately
    returns neither (see the enquiry route).
    """
    emails: list[str] = []
    yield emails
    async with AsyncSessionLocal() as db:
        for email in emails:
            rows = (
                (await db.execute(select(Lead).where(Lead.contact_email == email)))
                .scalars()
                .all()
            )
            for lead in rows:
                for table in (Communication, LeadStageEvent):
                    column = (
                        table.subject_id if table is Communication else table.lead_id
                    )
                    for child in (
                        (await db.execute(select(table).where(column == lead.id)))
                        .scalars()
                        .all()
                    ):
                        await db.delete(child)
                await db.flush()
                await db.delete(lead)
        await db.commit()


async def _place(client: AsyncClient, headers: dict, **over) -> dict:
    body = {
        "name": f"Test Coast {uuid.uuid4().hex[:8]}",
        "type": "beach",
        "country": "Kenya",
        "region": "Coast",
        "description": "Invented test destination.",
        "latitude": "-4.3",
        "longitude": "39.5",
    }
    body.update(over)
    resp = await client.post(f"{V1}/destinations", headers=headers, json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _property(client: AsyncClient, headers: dict, place: dict, **over) -> dict:
    body = {
        "name": f"Test House {uuid.uuid4().hex[:8]}",
        "destination_id": place["id"],
        "category": "lodge",
        "star_rating": 4,
        "description": "Invented test property.",
        "latitude": "-4.31",
        "longitude": "39.51",
        "check_in_time": "14:00",
        "check_out_time": "10:00",
        "website": "https://example.invalid",
    }
    body.update(over)
    resp = await client.post(f"{V1}/accommodations", headers=headers, json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


# --------------------------------------------------------------------------- #
# Nothing is public until somebody says so
# --------------------------------------------------------------------------- #


async def test_a_new_catalogue_row_is_not_on_the_website(
    client: AsyncClient, admin_tokens: dict
):
    """The default that matters.

    The catalogue holds every property the business has ever contracted with,
    including the ones it does not want to advertise. ``is_published`` starts
    false on every row, existing ones included.
    """
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)

    listed = await client.get(f"{V1}/public/destinations")
    assert listed.status_code == 200
    assert place["slug"] not in [one["slug"] for one in listed.json()]

    direct = await client.get(f"{V1}/public/destinations/{place['slug']}")
    assert direct.status_code == 404


async def test_publishing_takes_a_permission_of_its_own(
    client: AsyncClient, admin_tokens: dict
):
    """Loading a rate sheet must not be able to advertise forty hotels."""
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)

    email = unique_email("nopublish")
    created = await client.post(
        f"{V1}/users",
        headers=headers,
        json={
            "email": email,
            "password": "Passw0rd!123",
            "full_name": "Rate Loader",
            "role_keys": ["sales_agent"],
        },
    )
    assert created.status_code == 201, created.text
    tokens = (
        await client.post(
            f"{V1}/auth/login", data={"username": email, "password": "Passw0rd!123"}
        )
    ).json()

    denied = await client.post(
        f"{V1}/catalogue/destination/{place['id']}/publish",
        headers=auth_headers(tokens),
    )
    assert denied.status_code == 403
    assert "catalogue:publish" in denied.json()["error"]["message"]


async def test_a_published_destination_appears_and_can_be_withdrawn(
    client: AsyncClient, admin_tokens: dict
):
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)

    published = await client.post(
        f"{V1}/catalogue/destination/{place['id']}/publish", headers=headers
    )
    assert published.status_code == 200, published.text
    assert published.json()["is_published"] is True
    assert published.json()["published_by"] is not None
    assert published.json()["published_at"] is not None

    listed = await client.get(f"{V1}/public/destinations")
    assert place["slug"] in [one["slug"] for one in listed.json()]

    withdrawn = await client.post(
        f"{V1}/catalogue/destination/{place['id']}/withdraw", headers=headers
    )
    assert withdrawn.status_code == 200
    assert withdrawn.json()["is_published"] is False
    # Left on the row on purpose: it records that this was once live, which is
    # the question somebody asks when a search engine still has the page.
    assert withdrawn.json()["published_at"] is not None

    gone = await client.get(f"{V1}/public/destinations/{place['slug']}")
    assert gone.status_code == 404


async def test_a_row_with_no_copy_cannot_be_published(
    client: AsyncClient, admin_tokens: dict
):
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers, description=None)
    refused = await client.post(
        f"{V1}/catalogue/destination/{place['id']}/publish", headers=headers
    )
    assert refused.status_code == 400
    assert "has no description" in refused.json()["error"]["message"]


async def test_something_we_cannot_sell_cannot_be_advertised(
    client: AsyncClient, admin_tokens: dict
):
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers, is_active=False)
    refused = await client.post(
        f"{V1}/catalogue/destination/{place['id']}/publish", headers=headers
    )
    assert refused.status_code == 400
    assert "cannot be sold" in refused.json()["error"]["message"]


async def test_deactivating_a_published_row_takes_its_page_down(
    client: AsyncClient, admin_tokens: dict
):
    """Published AND active, not either.

    A property that was published and has since been deactivated cannot be
    quoted, and a page for something the quote engine will refuse to price is
    a page that generates an apology.
    """
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    await client.post(
        f"{V1}/catalogue/destination/{place['id']}/publish", headers=headers
    )
    assert (
        await client.get(f"{V1}/public/destinations/{place['slug']}")
    ).status_code == 200

    await client.patch(
        f"{V1}/destinations/{place['id']}", headers=headers, json={"is_active": False}
    )
    assert (
        await client.get(f"{V1}/public/destinations/{place['slug']}")
    ).status_code == 404


async def test_a_thin_page_publishes_and_says_what_is_missing(
    client: AsyncClient, admin_tokens: dict
):
    """Reported, not refused: the photographs arrive on Thursday."""
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    resp = await client.post(
        f"{V1}/catalogue/destination/{place['id']}/publish", headers=headers
    )
    assert resp.status_code == 200
    codes = [one["code"] for one in resp.json()["concerns"]]
    assert "page_no_image" in codes

    review = await client.get(f"{V1}/catalogue/destination/thin-pages", headers=headers)
    assert review.status_code == 200
    assert place["id"] in [one["id"] for one in review.json()]


async def test_a_kind_that_has_no_public_page_is_refused(
    client: AsyncClient, admin_tokens: dict
):
    resp = await client.post(
        f"{V1}/catalogue/supplier/{uuid.uuid4()}/publish",
        headers=auth_headers(admin_tokens),
    )
    assert resp.status_code == 404
    assert "not something that can be published" in resp.json()["error"]["message"]


# --------------------------------------------------------------------------- #
# The allow-list, over the wire
# --------------------------------------------------------------------------- #


async def test_a_property_page_carries_no_supplier_and_no_price(
    client: AsyncClient, admin_tokens: dict
):
    """The response, not just the view model.

    A response model built from the ORM row would gain every column the table
    gains — which is the failure the allow-list exists to prevent, and it has
    to be true of the JSON a stranger receives.
    """
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    stay = await _property(client, headers, place)
    await client.post(
        f"{V1}/catalogue/destination/{place['id']}/publish", headers=headers
    )
    await client.post(
        f"{V1}/catalogue/accommodation/{stay['id']}/publish", headers=headers
    )

    page = await client.get(f"{V1}/public/accommodations/{stay['slug']}")
    assert page.status_code == 200, page.text
    body = page.json()
    assert body["name"] == stay["name"]
    assert body["destination"] == place["name"]
    for absent in ("supplier_id", "website", "images_json", "is_active", "id"):
        assert absent not in body
    assert "rate" not in page.text.lower()


async def test_a_destination_page_lists_what_is_published_there(
    client: AsyncClient, admin_tokens: dict
):
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    shown = await _property(client, headers, place)
    hidden = await _property(client, headers, place)
    await client.post(
        f"{V1}/catalogue/destination/{place['id']}/publish", headers=headers
    )
    await client.post(
        f"{V1}/catalogue/accommodation/{shown['id']}/publish", headers=headers
    )

    page = (await client.get(f"{V1}/public/destinations/{place['slug']}")).json()
    assert shown["name"] in page["stays"]
    # The one nobody published stays off its own destination's page too.
    assert hidden["name"] not in page["stays"]


async def test_properties_can_be_narrowed_to_a_destination(
    client: AsyncClient, admin_tokens: dict
):
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    stay = await _property(client, headers, place)
    await client.post(
        f"{V1}/catalogue/destination/{place['id']}/publish", headers=headers
    )
    await client.post(
        f"{V1}/catalogue/accommodation/{stay['id']}/publish", headers=headers
    )

    listed = await client.get(
        f"{V1}/public/accommodations", params={"destination": place["slug"]}
    )
    assert [one["slug"] for one in listed.json()] == [stay["slug"]]


async def test_the_public_page_shows_the_editable_blurb_over_the_description(
    client: AsyncClient, admin_tokens: dict
):
    """``blurb`` had no write path in this API until §6.1.

    It has been read by the proposal layer since §3 and written by nothing but
    the demo seeder, so the paragraph under every property photograph was
    unreachable. A website made that unignorable.
    """
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    stay = await _property(client, headers, place)
    patched = await client.patch(
        f"{V1}/accommodations/{stay['id']}",
        headers=headers,
        json={"blurb": "Thatched bandas above the reef."},
    )
    assert patched.status_code == 200, patched.text

    await client.post(
        f"{V1}/catalogue/destination/{place['id']}/publish", headers=headers
    )
    await client.post(
        f"{V1}/catalogue/accommodation/{stay['id']}/publish", headers=headers
    )
    page = (await client.get(f"{V1}/public/accommodations/{stay['slug']}")).json()
    assert page["description"] == "Thatched bandas above the reef."


async def test_an_image_on_an_unpublished_property_is_not_readable(
    client: AsyncClient, admin_tokens: dict
):
    """An id is not a secret.

    Without the parent check this endpoint would be an unauthenticated read of
    every photograph in the system.
    """
    resp = await client.get(f"{V1}/public/images/accommodation/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["error"]["message"] == "No such image."


# --------------------------------------------------------------------------- #
# The one write
# --------------------------------------------------------------------------- #


async def test_an_enquiry_becomes_a_lead_and_a_logged_inbound_message(
    client: AsyncClient, admin_tokens: dict, swept_enquiries: list
):
    """What §6.1 exists for, end to end.

    Not its own table: an enquiry is a lead at the arrival stage (§5.2) and an
    inbound entry in the contact log (§5.3), both of which already have a
    morning list and a first-response measurement built on them.
    """
    email = unique_email("enquiry").replace("+", "")
    swept_enquiries.append(email)
    resp = await client.post(
        f"{V1}/public/enquiries",
        json={
            "name": "Amina Yusuf",
            "email": email,
            "destination": "Diani",
            "pax": 4,
            "message": "Two adults and two children, somewhere on the beach.",
            "page": "/destinations/diani",
        },
    )
    assert resp.status_code == 202, resp.text
    # No reference and no id: the id of a lead is the id of a row in the sales
    # pipeline, handed to whoever asked.
    assert set(resp.json()) == {"received", "message"}

    headers = auth_headers(admin_tokens)
    leads = (
        await client.get(f"{V1}/leads", headers=headers, params={"source": "website"})
    ).json()
    mine = [one for one in leads if one["contact_email"] == email]
    assert mine, leads
    lead = mine[0]
    assert lead["source"] == "website"
    assert lead["source_detail"] == "/destinations/diani"
    # A stranger's form does not choose whose deal it is or how far along.
    assert lead["owner_id"] is None
    assert lead["destination_interest"] == "Diani"
    assert lead["pax_estimate"] == 4

    log = (
        await client.get(f"{V1}/leads/{lead['id']}/communications", headers=headers)
    ).json()
    assert log["summary"]["contacts"] == 1
    # Nobody has replied yet, and the clock says so rather than saying zero.
    assert log["first_response_hours"] is None
    entry = log["entries"][0]
    assert entry["direction"] == "inbound"
    assert entry["channel"] == "website"
    assert "Two adults and two children" in entry["body"]
    assert "Enquired from: /destinations/diani" in entry["body"]


async def test_an_unanswered_website_enquiry_is_top_of_the_morning_list(
    client: AsyncClient, admin_tokens: dict, swept_enquiries: list
):
    """The trap §6.1 walked into, and the reason the rule changed.

    The enquiry logs the client's own words the moment it lands, which stamps
    "last contacted". Measured that way, every enquiry from the front door
    would look answered before a human had read it — so the rule now measures
    whether *we* have replied.
    """
    email = unique_email("unanswered").replace("+", "")
    swept_enquiries.append(email)
    await client.post(
        f"{V1}/public/enquiries",
        json={"name": "Never Answered", "email": email, "message": "Hello?"},
    )
    headers = auth_headers(admin_tokens)
    attention = (await client.get(f"{V1}/leads/attention", headers=headers)).json()
    mine = [one for one in attention if one["lead"]["contact_email"] == email]
    assert mine, "the enquiry nobody answered is missing from /leads/attention"
    reasons = mine[0]["reasons"]
    assert reasons[0]["code"] == "lead_never_contacted"
    assert "has written and nobody has replied" in reasons[0]["message"]


async def test_a_form_with_no_way_to_answer_it_is_refused(client: AsyncClient):
    resp = await client.post(
        f"{V1}/public/enquiries", json={"name": "Anonymous", "message": "Prices?"}
    )
    assert resp.status_code == 400
    assert "no way to answer you" in resp.json()["error"]["message"]


async def test_a_trapped_enquiry_gets_the_same_answer_and_no_lead(
    client: AsyncClient, admin_tokens: dict, swept_enquiries: list
):
    """Telling a bot which field to leave alone next time teaches it."""
    email = unique_email("trapped").replace("+", "")
    swept_enquiries.append(email)
    resp = await client.post(
        f"{V1}/public/enquiries",
        json={
            "name": "Spam Bot",
            "email": email,
            "message": "buy links",
            "trap": "http://spam.invalid",
        },
    )
    assert resp.status_code == 202
    assert resp.json()["received"] is True

    headers = auth_headers(admin_tokens)
    leads = (await client.get(f"{V1}/leads", headers=headers)).json()
    assert email not in [one["contact_email"] for one in leads]


async def test_the_enquiry_form_needs_no_login(
    client: AsyncClient, swept_enquiries: list
):
    """Stated as a test because it is the first such route in the platform."""
    email = unique_email("nologin").replace("+", "")
    swept_enquiries.append(email)
    resp = await client.post(
        f"{V1}/public/enquiries",
        json={"name": "Passer By", "phone": "+254700000000", "email": email},
    )
    assert resp.status_code == 202


async def test_the_public_reads_need_no_login(client: AsyncClient):
    for path in ("destinations", "accommodations", "activities"):
        resp = await client.get(f"{V1}/public/{path}")
        assert resp.status_code == 200, path
        assert isinstance(resp.json(), list)
