"""M-Pesa STK push, and the callback Safaricom sends back (§7.5).

Two very different callers use this router. The push itself is staff-only,
on the same ``booking:record_payment`` permission a manually recorded payment
already needs — collecting money is collecting money, regardless of which
button did it. The callback is **Safaricom's own server**, which carries no
bearer token and never will; its only credential is a ``CheckoutRequestID``
this system minted itself when the push was sent, which is exactly the check
:meth:`app.modules.mpesa.service.MpesaService.settle` makes. See that
method's own docstring for what protects it, and app.core.limits for why the
route is rate-limited on top of that.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import require_permission
from app.core.errors import NotFoundError
from app.core.limits import rate_limit
from app.db.session import get_db
from app.integrations.mpesa import MpesaClient, get_mpesa_client, parse_stk_callback
from app.modules.mpesa.schemas import (
    MpesaTransactionRead,
    StkPushAcceptedRead,
    StkPushCreate,
)
from app.modules.mpesa.service import MpesaService
from app.modules.users.models import User

router = APIRouter(tags=["mpesa"])


async def _owned(db, booking_id: uuid.UUID, transaction_id: uuid.UUID):
    """A transaction, but only if it actually belongs to this booking.

    Without this check, anyone with read access to *some* booking could
    fetch a push against a different one just by guessing its id in the
    URL — the id is a plain path parameter, not a secret, so the ownership
    check has to be explicit rather than assumed from the URL shape.
    """
    transaction = await MpesaService(db).get(transaction_id)
    if transaction.booking_id != booking_id:
        raise NotFoundError("No such M-Pesa transaction on this booking.")
    return transaction

READ = "booking:read"
PAY = "booking:record_payment"

_callback_limit = Depends(
    rate_limit(bucket="mpesa_callback", limit=settings.PUBLIC_READ_PER_MINUTE, seconds=60)
)


@router.post(
    "/bookings/{booking_id}/payments/mpesa",
    response_model=StkPushAcceptedRead,
    status_code=202,
)
async def push_stk(
    booking_id: uuid.UUID,
    body: StkPushCreate,
    db: AsyncSession = Depends(get_db),
    client: MpesaClient = Depends(get_mpesa_client),
    actor: User = Depends(require_permission(PAY)),
):
    """Prompt a customer's phone for their M-Pesa PIN.

    **202, not 200 or 201** — deliberately: this only confirms Safaricom has
    queued the prompt, not that the customer has paid. Poll
    ``GET .../mpesa/{transaction_id}`` or wait for the callback to find out
    what actually happened.
    """
    transaction = await MpesaService(db, client=client).initiate(
        booking_id,
        phone_number=body.phone_number,
        amount=body.amount,
        instalment_id=body.instalment_id,
        actor_id=actor.id,
    )
    return StkPushAcceptedRead(
        transaction_id=transaction.id,
        customer_message=(
            "The customer's phone has been prompted for their M-Pesa PIN."
        ),
    )


@router.get(
    "/bookings/{booking_id}/payments/mpesa/{transaction_id}",
    response_model=MpesaTransactionRead,
)
async def get_stk_push(
    booking_id: uuid.UUID,
    transaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(READ)),
):
    """Where a push stands right now — pending, completed, or failed.

    A plain read against this system's own record, with no call out to
    Daraja: use the ``/refresh`` action below to actually ask Safaricom
    again for a push whose callback seems to have gone missing.
    """
    return await _owned(db, booking_id, transaction_id)


@router.post(
    "/bookings/{booking_id}/payments/mpesa/{transaction_id}/refresh",
    response_model=MpesaTransactionRead,
)
async def refresh_stk_push(
    booking_id: uuid.UUID,
    transaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    client: MpesaClient = Depends(get_mpesa_client),
    _: User = Depends(require_permission(PAY)),
):
    """Ask Daraja directly, for a push whose callback never arrived.

    Safaricom's own documentation recommends this as the fallback when a
    callback goes missing — a firewall, a deploy mid-flight, a transient
    network fault on either side. A no-op for a transaction already settled.
    """
    await _owned(db, booking_id, transaction_id)
    return await MpesaService(db, client=client).refresh_from_daraja(transaction_id)


@router.post("/integrations/mpesa/callback", dependencies=[_callback_limit])
async def mpesa_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Where Safaricom tells us what happened, unauthenticated by design.

    There is no bearer token to check — Safaricom's own servers call this,
    carrying nothing but the result and the ``CheckoutRequestID`` it minted
    when the push was sent. That ID is the only credential this endpoint
    can check, and it is exactly what ``MpesaService.settle`` matches
    against a transaction this system actually initiated: a request quoting
    an ID nobody recognises settles nothing and 200s anyway, the same answer
    Safaricom gets whether the ID was real or guessed, since telling the two
    apart in the response would hand a prober a way to enumerate valid ones.

    Always 200. Daraja retries a callback that does not get one, and a retry
    storm over a transaction this system has already decided about (or never
    recognised) helps nobody.
    """
    payload = await request.json()
    try:
        result = parse_stk_callback(payload)
    except Exception:  # noqa: BLE001 — a malformed callback is not our bug to raise on
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

    await MpesaService(db).settle(result, today=datetime.now(UTC).date())
    return {"ResultCode": 0, "ResultDesc": "Accepted"}
