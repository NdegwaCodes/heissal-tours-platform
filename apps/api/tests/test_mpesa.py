"""The M-Pesa STK push flow: service, and the four routes on top of it (§7.5).

No real Daraja call anywhere in here — ``_FakeMpesaClient`` stands in for
:class:`app.integrations.mpesa.MpesaClient` in every test, so this suite runs
with no network and no credentials, the same as production will until the
four secret settings are filled in. The pure arithmetic
(``normalise_phone``, ``stk_password``, ``whole_kes``, ``parse_stk_callback``)
has its own tests in ``test_mpesa_integration.py``.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.integrations.mpesa import MpesaError, StkPushAccepted, StkPushResult, get_mpesa_client
from app.main import app
from app.modules.bookings.models import Booking
from app.modules.mpesa.models import COMPLETED, FAILED, PENDING, MpesaTransaction
from app.modules.mpesa.service import MpesaService
from app.modules.quotes.models import Quote, QuoteOption
from tests.conftest import unique_email

API = settings.API_V1_STR
pytestmark = pytest.mark.asyncio(loop_scope="session")

D = Decimal
TODAY = date.today()
ARRIVAL = TODAY + timedelta(days=60)
DEPARTURE = ARRIVAL + timedelta(days=3)


def _h(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@dataclass
class _FakeMpesaClient:
    """Stands in for :class:`MpesaClient` — no network, fully scripted.

    ``push_error`` lets a test make the initiate call itself fail (a bad
    phone number reaching Daraja, an amount below their minimum); the
    query queue is a list because :meth:`refresh_from_daraja` can be
    exercised more than once per test.
    """

    push_error: Exception | None = None
    query_results: list[StkPushResult] = field(default_factory=list)
    query_errors: list[Exception | None] = field(default_factory=list)
    pushes: list[dict] = field(default_factory=list)

    async def initiate_stk_push(self, **kwargs) -> StkPushAccepted:
        self.pushes.append(kwargs)
        if self.push_error:
            raise self.push_error
        return StkPushAccepted(
            merchant_request_id=f"merchant-{uuid.uuid4().hex[:8]}",
            checkout_request_id=f"ws_CO_{uuid.uuid4().hex[:12]}",
            customer_message="Please enter your M-Pesa PIN.",
        )

    async def query_stk_push(self, *, checkout_request_id, now) -> StkPushResult:
        if self.query_errors:
            error = self.query_errors.pop(0)
            if error:
                raise error
        if self.query_results:
            return self.query_results.pop(0)
        raise MpesaError("no scripted result for this test")


@pytest_asyncio.fixture(loop_scope="session")
async def booked_away():
    """Remove the quotes (and their bookings) this module created."""
    made: list[str] = []
    yield made
    async with AsyncSessionLocal() as db:
        for quote_id in made:
            bookings = (
                (await db.execute(select(Booking).where(Booking.quote_id == uuid.UUID(quote_id))))
                .scalars()
                .all()
            )
            for booking in bookings:
                await db.delete(booking)
            await db.flush()
            row = await db.get(Quote, uuid.UUID(quote_id))
            if row is not None:
                await db.delete(row)
        await db.commit()


async def _booked(client, h, ids, made):
    """A confirmed-eligible booking: an accepted, issued, priced quote, booked."""
    record = await client.post(
        f"{API}/clients",
        headers=h,
        json={
            "name": f"Mpesa Co {uuid.uuid4().hex[:8]}",
            "email": unique_email("mpesa"),
            "residence_category_id": ids["residence_citizen"],
        },
    )
    assert record.status_code == 201, record.text
    created = await client.post(
        f"{API}/quotes",
        headers=h,
        json={
            "client_id": record.json()["id"],
            "presentation_currency": "KES",
            "residence_category_id": ids["residence_citizen"],
            "arrival_date": ARRIVAL.isoformat(),
            "departure_date": DEPARTURE.isoformat(),
            "pax_count": 2,
            "requested_meal_plan_id": ids["meal_plan_fb"],
            "options": [{"accommodation_id": ids["acc_sto_full_board"], "is_recommended": True}],
        },
    )
    assert created.status_code == 201, created.text
    quote = created.json()
    made.append(quote["id"])
    priced = await client.post(f"{API}/quotes/{quote['id']}/options/price", headers=h)
    assert priced.status_code == 200, priced.text
    issued = await client.post(f"{API}/quotes/{quote['id']}/issue", headers=h)
    assert issued.status_code == 200, issued.text

    async with AsyncSessionLocal() as db:
        option_id = (
            (
                await db.execute(
                    select(QuoteOption.id).where(
                        QuoteOption.quote_id == uuid.UUID(quote["id"])
                    )
                )
            )
            .scalars()
            .first()
        )
    accepted = await client.post(
        f"{API}/quotes/{quote['id']}/accept", headers=h, json={"option_id": str(option_id)}
    )
    assert accepted.status_code == 200, accepted.text

    booked = await client.post(f"{API}/quotes/{quote['id']}/booking", headers=h, json={})
    assert booked.status_code == 201, booked.text
    return booked.json()


# --------------------------------------------------------------------------- #
# MpesaService — direct, with a fake client
# --------------------------------------------------------------------------- #


async def test_initiating_a_push_persists_a_pending_transaction(
    client, admin_tokens, sample_catalogue, booked_away
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    fake = _FakeMpesaClient()
    async with AsyncSessionLocal() as db:
        transaction = await MpesaService(db, client=fake).initiate(
            uuid.UUID(booking["id"]),
            phone_number="0712345678",
            amount=D(booking["instalments"][0]["amount"]),
        )
    assert transaction.status == PENDING
    assert transaction.phone_number == "254712345678"
    assert transaction.checkout_request_id
    assert fake.pushes[0]["account_reference"] == booking["reference"]


async def test_a_cancelled_booking_refuses_a_push(
    client, admin_tokens, sample_catalogue, booked_away
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    cancelled = await client.post(
        f"{API}/bookings/{booking['id']}/cancel",
        headers=h,
        json={"reason": "Client changed plans."},
    )
    assert cancelled.status_code == 200, cancelled.text

    async with AsyncSessionLocal() as db:
        with pytest.raises(Exception, match="cancelled"):
            await MpesaService(db, client=_FakeMpesaClient()).initiate(
                uuid.UUID(booking["id"]), phone_number="0712345678", amount=D("1000")
            )


async def test_a_non_kes_booking_is_refused_not_converted(
    client, admin_tokens, sample_catalogue, booked_away
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    async with AsyncSessionLocal() as db:
        row = await db.get(Booking, uuid.UUID(booking["id"]))
        row.currency = "USD"
        await db.commit()

        with pytest.raises(Exception, match="Kenyan shillings"):
            await MpesaService(db, client=_FakeMpesaClient()).initiate(
                uuid.UUID(booking["id"]), phone_number="0712345678", amount=D("1000")
            )


async def test_settling_a_successful_result_records_a_payment_and_links_it(
    client, admin_tokens, sample_catalogue, booked_away
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    deposit = D(booking["instalments"][0]["amount"])
    fake = _FakeMpesaClient()
    async with AsyncSessionLocal() as db:
        transaction = await MpesaService(db, client=fake).initiate(
            uuid.UUID(booking["id"]), phone_number="0712345678", amount=deposit,
            instalment_id=uuid.UUID(booking["instalments"][0]["id"]),
        )
        checkout_id = transaction.checkout_request_id

    result = StkPushResult(
        checkout_request_id=checkout_id,
        result_code=0,
        result_desc="The service request is processed successfully.",
        amount=deposit,
        mpesa_receipt_number=f"REC{uuid.uuid4().hex[:7].upper()}",
    )
    async with AsyncSessionLocal() as db:
        settled = await MpesaService(db).settle(result, today=TODAY)
        assert settled.status == COMPLETED
        assert settled.payment_id is not None
        assert settled.mpesa_receipt_number == result.mpesa_receipt_number

    position = (await client.get(f"{API}/bookings/{booking['id']}/owed", headers=h)).json()
    assert D(position["paid"]) == deposit


async def test_settling_a_failed_result_marks_the_transaction_failed(
    client, admin_tokens, sample_catalogue, booked_away
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    fake = _FakeMpesaClient()
    async with AsyncSessionLocal() as db:
        transaction = await MpesaService(db, client=fake).initiate(
            uuid.UUID(booking["id"]), phone_number="0712345678", amount=D("1000")
        )
        checkout_id = transaction.checkout_request_id

    result = StkPushResult(
        checkout_request_id=checkout_id, result_code=1032, result_desc="Request cancelled by user."
    )
    async with AsyncSessionLocal() as db:
        settled = await MpesaService(db).settle(result)
        assert settled.status == FAILED
        assert settled.payment_id is None


async def test_a_repeated_callback_settles_only_once(
    client, admin_tokens, sample_catalogue, booked_away
):
    """Idempotency: the second callback for one push must not create a second Payment."""
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    fake = _FakeMpesaClient()
    async with AsyncSessionLocal() as db:
        transaction = await MpesaService(db, client=fake).initiate(
            uuid.UUID(booking["id"]), phone_number="0712345678", amount=D("1000")
        )
        checkout_id = transaction.checkout_request_id

    result = StkPushResult(
        checkout_request_id=checkout_id,
        result_code=0,
        result_desc="ok",
        amount=D("1000"),
        mpesa_receipt_number=f"REC{uuid.uuid4().hex[:7].upper()}",
    )
    async with AsyncSessionLocal() as db:
        first = await MpesaService(db).settle(result)
        payment_id = first.payment_id

    async with AsyncSessionLocal() as db:
        second = await MpesaService(db).settle(result)
        assert second.payment_id == payment_id

    async with AsyncSessionLocal() as db:
        rows = (
            (
                await db.execute(
                    select(MpesaTransaction).where(
                        MpesaTransaction.checkout_request_id == checkout_id
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(rows) == 1


async def test_settling_an_unrecognised_checkout_id_does_nothing(client):
    """A forged or stale callback quoting an id nobody minted settles nothing."""
    async with AsyncSessionLocal() as db:
        result = StkPushResult(
            checkout_request_id="ws_CO_nonexistent", result_code=0, result_desc="ok"
        )
        assert await MpesaService(db).settle(result) is None


async def test_refreshing_a_pending_push_asks_daraja_and_settles(
    client, admin_tokens, sample_catalogue, booked_away
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    fake = _FakeMpesaClient()
    async with AsyncSessionLocal() as db:
        transaction = await MpesaService(db, client=fake).initiate(
            uuid.UUID(booking["id"]), phone_number="0712345678", amount=D("1000")
        )
        transaction_id, checkout_id = transaction.id, transaction.checkout_request_id

    fake.query_results.append(
        StkPushResult(
            checkout_request_id=checkout_id,
            result_code=0,
            result_desc="ok",
            amount=D("1000"),
            mpesa_receipt_number=f"REC{uuid.uuid4().hex[:7].upper()}",
        )
    )
    async with AsyncSessionLocal() as db:
        refreshed = await MpesaService(db, client=fake).refresh_from_daraja(transaction_id)
        assert refreshed.status == COMPLETED


async def test_refreshing_when_daraja_still_says_processing_stays_pending(
    client, admin_tokens, sample_catalogue, booked_away
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    fake = _FakeMpesaClient()
    async with AsyncSessionLocal() as db:
        transaction = await MpesaService(db, client=fake).initiate(
            uuid.UUID(booking["id"]), phone_number="0712345678", amount=D("1000")
        )
        transaction_id = transaction.id

    fake.query_errors.append(MpesaError("still being processed"))
    async with AsyncSessionLocal() as db:
        refreshed = await MpesaService(db, client=fake).refresh_from_daraja(transaction_id)
        assert refreshed.status == PENDING


async def test_a_service_call_needing_a_client_refuses_clearly_without_one(
    client, admin_tokens, sample_catalogue, booked_away
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    async with AsyncSessionLocal() as db:
        with pytest.raises(RuntimeError, match="needs an MpesaClient"):
            await MpesaService(db).initiate(
                uuid.UUID(booking["id"]), phone_number="0712345678", amount=D("1000")
            )


# --------------------------------------------------------------------------- #
# The four routes
# --------------------------------------------------------------------------- #


@pytest_asyncio.fixture(loop_scope="session")
async def fake_mpesa():
    """Override the app's Daraja dependency with a scripted fake for one test."""
    fake = _FakeMpesaClient()
    app.dependency_overrides[get_mpesa_client] = lambda: fake
    yield fake
    del app.dependency_overrides[get_mpesa_client]


async def test_pushing_stk_via_the_api_returns_202_and_a_transaction_id(
    client, admin_tokens, sample_catalogue, booked_away, fake_mpesa
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    pushed = await client.post(
        f"{API}/bookings/{booking['id']}/payments/mpesa",
        headers=h,
        json={"phone_number": "0712345678", "amount": booking["instalments"][0]["amount"]},
    )
    assert pushed.status_code == 202, pushed.text
    assert pushed.json()["transaction_id"]


async def test_getting_a_push_by_id_reads_its_current_status(
    client, admin_tokens, sample_catalogue, booked_away, fake_mpesa
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    pushed = await client.post(
        f"{API}/bookings/{booking['id']}/payments/mpesa",
        headers=h,
        json={"phone_number": "0712345678", "amount": "1000"},
    )
    transaction_id = pushed.json()["transaction_id"]
    fetched = await client.get(
        f"{API}/bookings/{booking['id']}/payments/mpesa/{transaction_id}", headers=h
    )
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["status"] == "pending"


async def test_a_push_cannot_be_fetched_through_a_different_booking(
    client, admin_tokens, sample_catalogue, booked_away, fake_mpesa
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking_a = await _booked(client, h, ids, booked_away)
    booking_b = await _booked(client, h, ids, booked_away)
    pushed = await client.post(
        f"{API}/bookings/{booking_a['id']}/payments/mpesa",
        headers=h,
        json={"phone_number": "0712345678", "amount": "1000"},
    )
    transaction_id = pushed.json()["transaction_id"]

    wrong = await client.get(
        f"{API}/bookings/{booking_b['id']}/payments/mpesa/{transaction_id}", headers=h
    )
    assert wrong.status_code == 404, wrong.text

    refreshed = await client.post(
        f"{API}/bookings/{booking_b['id']}/payments/mpesa/{transaction_id}/refresh", headers=h
    )
    assert refreshed.status_code == 404, refreshed.text


async def test_refreshing_via_the_api_settles_a_completed_push(
    client, admin_tokens, sample_catalogue, booked_away, fake_mpesa
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    pushed = await client.post(
        f"{API}/bookings/{booking['id']}/payments/mpesa",
        headers=h,
        json={"phone_number": "0712345678", "amount": "1000"},
    )
    transaction_id = pushed.json()["transaction_id"]
    async with AsyncSessionLocal() as db:
        row = await db.get(MpesaTransaction, uuid.UUID(transaction_id))
        checkout_id = row.checkout_request_id

    fake_mpesa.query_results.append(
        StkPushResult(
            checkout_request_id=checkout_id,
            result_code=0,
            result_desc="ok",
            amount=D("1000"),
            mpesa_receipt_number=f"REC{uuid.uuid4().hex[:7].upper()}",
        )
    )
    refreshed = await client.post(
        f"{API}/bookings/{booking['id']}/payments/mpesa/{transaction_id}/refresh", headers=h
    )
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()["status"] == "completed"


async def test_the_callback_endpoint_always_answers_200_even_for_junk(client):
    response = await client.post(f"{API}/integrations/mpesa/callback", json={"garbage": True})
    assert response.status_code == 200, response.text
    assert response.json()["ResultCode"] == 0


async def test_the_callback_endpoint_settles_a_real_transaction(
    client, admin_tokens, sample_catalogue, booked_away, fake_mpesa
):
    h, ids = _h(admin_tokens), sample_catalogue
    booking = await _booked(client, h, ids, booked_away)
    pushed = await client.post(
        f"{API}/bookings/{booking['id']}/payments/mpesa",
        headers=h,
        json={"phone_number": "0712345678", "amount": "1000"},
    )
    transaction_id = pushed.json()["transaction_id"]
    async with AsyncSessionLocal() as db:
        row = await db.get(MpesaTransaction, uuid.UUID(transaction_id))
        checkout_id = row.checkout_request_id

    callback_payload = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-1",
                "CheckoutRequestID": checkout_id,
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 1000},
                        {"Name": "MpesaReceiptNumber", "Value": "NLJ7RT61SV"},
                        {"Name": "TransactionDate", "Value": 20260913144950},
                        {"Name": "PhoneNumber", "Value": 254712345678},
                    ]
                },
            }
        }
    }
    response = await client.post(f"{API}/integrations/mpesa/callback", json=callback_payload)
    assert response.status_code == 200, response.text

    fetched = await client.get(
        f"{API}/bookings/{booking['id']}/payments/mpesa/{transaction_id}", headers=h
    )
    assert fetched.json()["status"] == "completed"
    assert fetched.json()["mpesa_receipt_number"] == "NLJ7RT61SV"
