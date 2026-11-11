"""``POST /public/estimate``, over HTTP (§6.3).

Properties and figures are invented, as everywhere in this suite. No supplier
contract rate appears in this repository.

These tests build their own throwaway destination, property, room type and
rate rather than using ``sample_catalogue`` — the same reason ``test_public.py``
does: publishing (and, here, rate creation) mutates rows a shared read-mostly
fixture cannot afford to have mutated under it.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.core.config import settings
from tests.conftest import auth_headers

pytestmark = pytest.mark.asyncio(loop_scope="session")

V1 = settings.API_V1_STR
D = Decimal


async def _place(client: AsyncClient, headers: dict) -> dict:
    body = {
        "name": f"Estimate Coast {uuid.uuid4().hex[:8]}",
        "type": "beach",
        "country": "Kenya",
        "region": "Coast",
        "description": "Invented test destination.",
    }
    resp = await client.post(f"{V1}/destinations", headers=headers, json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _residence_id(client: AsyncClient, headers: dict, key: str) -> str:
    listed = (
        await client.get(f"{V1}/residence-categories", headers=headers)
    ).json()
    found = next(row for row in listed if row["key"] == key)
    return found["id"]


async def _meal_plan_id(client: AsyncClient, headers: dict, code: str) -> str:
    listed = (await client.get(f"{V1}/meal-plans", headers=headers)).json()
    found = next(row for row in listed if row["code"] == code)
    return found["id"]


async def _published_property(
    client: AsyncClient,
    headers: dict,
    place: dict,
    *,
    star_rating: int,
    rate_per_night: str,
    currency: str = "KES",
    occupancy: int = 2,
    residence_key: str = "non_resident",
    meal_plan_code: str = "BB",
) -> dict:
    """A property in ``place``, published, active, with one current BB rate."""
    body = {
        "name": f"Estimate House {uuid.uuid4().hex[:8]}",
        "destination_id": place["id"],
        "category": "lodge",
        "star_rating": star_rating,
        "description": "Invented test property.",
        "blurb": "Invented test property.",
    }
    stay = (
        await client.post(f"{V1}/accommodations", headers=headers, json=body)
    ).json()

    room = (
        await client.post(
            f"{V1}/accommodations/{stay['id']}/room-types",
            headers=headers,
            json={"name": "Garden Twin", "max_occupancy": occupancy},
        )
    ).json()

    residence_id = await _residence_id(client, headers, residence_key)
    meal_plan_id = await _meal_plan_id(client, headers, meal_plan_code)

    rate_body = {
        "room_type_id": room["id"],
        "meal_plan_id": meal_plan_id,
        "residence_category_id": residence_id,
        "effective_from": str(date.today() - timedelta(days=1)),
        "effective_to": str(date.today() + timedelta(days=365)),
        "currency": currency,
        "rate_per_night": rate_per_night,
        "occupancy": occupancy,
    }
    created = await client.post(
        f"{V1}/accommodations/{stay['id']}/rates", headers=headers, json=rate_body
    )
    assert created.status_code == 201, created.text

    published = await client.post(
        f"{V1}/catalogue/destination/{place['id']}/publish", headers=headers
    )
    assert published.status_code == 200, published.text
    published = await client.post(
        f"{V1}/catalogue/accommodation/{stay['id']}/publish", headers=headers
    )
    assert published.status_code == 200, published.text
    return stay


# --------------------------------------------------------------------------- #
# A real leg, priced off a real rate
# --------------------------------------------------------------------------- #


async def test_a_published_property_with_a_current_rate_prices_a_leg(
    client: AsyncClient, admin_tokens: dict
):
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    stay = await _published_property(
        client, headers, place, star_rating=4, rate_per_night="16000"
    )

    resp = await client.post(
        f"{V1}/public/estimate",
        json={
            "resident": False,
            "adults": 2,
            "children": 0,
            "legs": [{"destination": place["slug"], "tier": "luxury", "nights": 3}],
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    leg = body["legs"][0]
    assert leg["refused"] is None
    assert leg["property_name"] == stay["name"]
    assert leg["room_type"] == "Garden Twin"
    assert leg["meal_plan"] == "BB"
    assert leg["currency"] == "KES"

    # The build-up is the real one (app.modules.quotes.options.build_up), by
    # hand: 16000/night * 3 nights = 48000 cost, +5% contingency = 50400,
    # +24% profit = 62496, rounded up to the nearest 100 per person (2 pax).
    assert leg["per_person"] == "31300.00" or leg["per_person"] == "31300"
    assert body["currency"] == "KES"
    assert body["per_person"] == leg["per_person"]
    assert "Indicative only" in body["note"]


async def test_the_response_never_carries_a_quote_reference(
    client: AsyncClient, admin_tokens: dict
):
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    await _published_property(client, headers, place, star_rating=4, rate_per_night="16000")

    resp = await client.post(
        f"{V1}/public/estimate",
        json={
            "adults": 2,
            "legs": [{"destination": place["slug"], "tier": "luxury", "nights": 2}],
        },
    )
    body = resp.json()
    assert "reference" not in body
    assert "quote_id" not in body
    assert "valid_until" not in body


# --------------------------------------------------------------------------- #
# Refusing rather than inventing
# --------------------------------------------------------------------------- #


async def test_a_destination_with_no_matching_tier_is_refused_by_leg(
    client: AsyncClient, admin_tokens: dict
):
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    # Only a 4-star (luxury) property exists here — nothing in "ultra".
    await _published_property(client, headers, place, star_rating=4, rate_per_night="16000")

    resp = await client.post(
        f"{V1}/public/estimate",
        json={
            "adults": 2,
            "legs": [{"destination": place["slug"], "tier": "ultra", "nights": 3}],
        },
    )
    assert resp.status_code == 200
    leg = resp.json()["legs"][0]
    assert leg["refused"] is not None
    assert leg["per_person"] is None
    assert leg["group_total"] is None


async def test_an_unpublished_property_cannot_be_priced(
    client: AsyncClient, admin_tokens: dict
):
    """The same rule as the read endpoints: published AND active, not either."""
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    stay = await _published_property(
        client, headers, place, star_rating=4, rate_per_night="16000"
    )
    await client.post(
        f"{V1}/catalogue/accommodation/{stay['id']}/withdraw", headers=headers
    )

    resp = await client.post(
        f"{V1}/public/estimate",
        json={
            "adults": 2,
            "legs": [{"destination": place["slug"], "tier": "luxury", "nights": 3}],
        },
    )
    leg = resp.json()["legs"][0]
    assert leg["refused"] is not None


async def test_an_unknown_destination_is_refused(client: AsyncClient):
    resp = await client.post(
        f"{V1}/public/estimate",
        json={
            "adults": 2,
            "legs": [{"destination": "not-a-real-place", "tier": "comfort", "nights": 2}],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["legs"][0]["refused"] is not None


async def test_an_unknown_tier_is_refused_before_any_lookup(client: AsyncClient):
    resp = await client.post(
        f"{V1}/public/estimate",
        json={
            "adults": 2,
            "legs": [{"destination": "anywhere", "tier": "premium", "nights": 2}],
        },
    )
    assert resp.status_code == 200
    leg = resp.json()["legs"][0]
    assert leg["refused"] is not None
    assert "comfort, luxury or ultra" in leg["refused"]


# --------------------------------------------------------------------------- #
# Currency never gets summed silently
# --------------------------------------------------------------------------- #


async def test_a_mixed_currency_trip_reports_legs_but_no_combined_total(
    client: AsyncClient, admin_tokens: dict
):
    headers = auth_headers(admin_tokens)
    kes_place = await _place(client, headers)
    usd_place = await _place(client, headers)
    await _published_property(
        client, headers, kes_place, star_rating=4, rate_per_night="16000", currency="KES"
    )
    await _published_property(
        client, headers, usd_place, star_rating=4, rate_per_night="180", currency="USD"
    )

    resp = await client.post(
        f"{V1}/public/estimate",
        json={
            "adults": 2,
            "legs": [
                {"destination": kes_place["slug"], "tier": "luxury", "nights": 2},
                {"destination": usd_place["slug"], "tier": "luxury", "nights": 2},
            ],
        },
    )
    body = resp.json()
    assert all(leg["refused"] is None for leg in body["legs"])
    assert body["currency"] is None
    assert body["per_person"] is None
    assert body["group_total"] is None


# --------------------------------------------------------------------------- #
# The residence category actually changes the rate used
# --------------------------------------------------------------------------- #


async def test_resident_and_non_resident_rates_are_kept_apart(
    client: AsyncClient, admin_tokens: dict
):
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    await _published_property(
        client, headers, place, star_rating=4, rate_per_night="16000",
        currency="KES", residence_key="non_resident",
    )
    # No "resident" rate filed at all for this property.
    resp = await client.post(
        f"{V1}/public/estimate",
        json={
            "resident": True,
            "adults": 2,
            "legs": [{"destination": place["slug"], "tier": "luxury", "nights": 2}],
        },
    )
    leg = resp.json()["legs"][0]
    assert leg["refused"] is not None


# --------------------------------------------------------------------------- #
# Bounds
# --------------------------------------------------------------------------- #


async def test_at_least_one_leg_is_required(client: AsyncClient):
    resp = await client.post(
        f"{V1}/public/estimate", json={"adults": 2, "legs": []}
    )
    assert resp.status_code == 422


async def test_the_estimate_endpoint_needs_no_login(
    client: AsyncClient, admin_tokens: dict
):
    """Stated as a test because it is the second unauthenticated write-shaped
    route in the platform, after the enquiry form."""
    headers = auth_headers(admin_tokens)
    place = await _place(client, headers)
    await _published_property(client, headers, place, star_rating=2, rate_per_night="9000")

    resp = await client.post(
        f"{V1}/public/estimate",
        json={
            "adults": 2,
            "legs": [{"destination": place["slug"], "tier": "comfort", "nights": 1}],
        },
    )
    assert resp.status_code == 200
