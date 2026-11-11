"""Bookings and payments over the API (§7.1).

``booking:record_payment`` is separate from managing a booking, deliberately.
Recording money is the act every audit turns on, and the person who books a
trip is not always the person who reconciles the bank.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_permission
from app.db.session import get_db
from app.modules.bookings.models import ACTIVE_STATUSES, Booking
from app.modules.bookings.schemas import (
    BookingCreate,
    BookingDueRead,
    BookingRead,
    CancelBooking,
    CancellationPreviewRead,
    CancellationSettlementRead,
    InstalmentRead,
    OwedRead,
    PaymentCreate,
    ScheduleLineRead,
)
from app.modules.bookings.service import BookingService
from app.modules.users.models import User

router = APIRouter(tags=["bookings"])

READ = "booking:read"
MANAGE = "booking:manage"
PAY = "booking:record_payment"


def _owed(position) -> OwedRead:
    return OwedRead(
        total=position.total,
        paid=position.paid,
        balance=position.balance,
        overpaid=position.overpaid,
        currency=position.currency,
        is_settled=position.is_settled,
        overdue=[_line(one) for one in position.overdue],
        next_due=_line(position.next_due) if position.next_due else None,
    )


def _line(one) -> ScheduleLineRead:
    return ScheduleLineRead(
        label=one.label,
        due_on=one.due_on,
        amount=one.amount,
        currency=one.currency,
    )


@router.post(
    "/quotes/{quote_id}/booking", response_model=BookingRead, status_code=201
)
async def create_booking(
    quote_id: uuid.UUID,
    body: BookingCreate,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(require_permission(MANAGE)),
):
    """Turn an accepted quote into a booking, with its payment schedule.

    Refused unless the quote is accepted: §5.1 records the sale and this is the
    operational record that follows it. Creating one from a quote nobody has
    accepted would put a trip in the operations list that no client agreed to.
    """
    return await BookingService(db).create_from_quote(
        quote_id,
        actor_id=actor.id,
        notes=body.notes,
        is_exclusive_use=body.is_exclusive_use,
    )


@router.get("/bookings", response_model=list[BookingRead])
async def list_bookings(
    status: str | None = Query(default=None),
    active_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(READ)),
):
    stmt = select(Booking)
    if status:
        stmt = stmt.where(Booking.status == status)
    if active_only:
        stmt = stmt.where(Booking.status.in_(ACTIVE_STATUSES))
    stmt = stmt.order_by(Booking.arrival_date).limit(500)
    return (await db.execute(stmt)).scalars().all()


@router.get("/bookings/due", response_model=list[BookingDueRead])
async def bookings_due(
    within_days: int = Query(default=7, ge=0, le=365),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(READ)),
):
    """Active bookings with something overdue or falling due soon.

    The operations equivalent of the leads' morning list (§5.2): an unpaid
    balance a fortnight before travel is a phone call, and a booking that
    reaches the airport unpaid is a loss.
    """
    found = await BookingService(db).due(within_days=within_days)
    return [
        BookingDueRead(booking=BookingRead.model_validate(booking), owed=_owed(position))
        for booking, position in found
    ]


@router.get("/bookings/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(READ)),
):
    return await BookingService(db).get(booking_id)


@router.get("/bookings/{booking_id}/owed", response_model=OwedRead)
async def booking_position(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(READ)),
):
    """What is paid, what is owed, what is overdue and what is overpaid."""
    return _owed(await BookingService(db).position(booking_id))


@router.post("/bookings/{booking_id}/payments", response_model=BookingRead)
async def record_payment(
    booking_id: uuid.UUID,
    body: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(require_permission(PAY)),
):
    """Record money that arrived. Confirms the booking once the deposit is in.

    On the **deposit**, not the balance: confirming is telling the suppliers it
    is happening, and that is what a deposit buys. Waiting for the balance
    would mean nothing is confirmed until a fortnight before travel.
    """
    return await BookingService(db).record_payment(
        booking_id,
        amount=body.amount,
        paid_on=body.paid_on,
        method=body.method,
        currency=body.currency,
        reference=body.reference,
        instalment_id=body.instalment_id,
        notes=body.notes,
        actor_id=actor.id,
    )


@router.get(
    "/bookings/{booking_id}/cancellation-preview",
    response_model=CancellationPreviewRead,
)
async def preview_cancellation(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(READ)),
):
    """What cancelling today would retain, without cancelling anything.

    A read, on the read permission — telling a client what it would cost is
    not the same act as actually stopping their trip.
    """
    service = BookingService(db)
    booking = await service.get(booking_id)
    found = await service.preview_cancellation(booking_id)
    return CancellationPreviewRead(
        notice_days=found.notice_days,
        band=found.band,
        is_peak=found.is_peak,
        is_group=found.is_group,
        retained_pct=found.retained_pct,
        retained_amount=found.retained_amount,
        currency=booking.currency,
        peak_label=found.peak_label,
    )


@router.get(
    "/bookings/{booking_id}/cancellation-settlement",
    response_model=CancellationSettlementRead,
)
async def cancellation_settlement(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(READ)),
):
    """Whether a cancelled booking is owed a refund or still owes money.

    Refused (400) for a booking that has not been cancelled — see
    ``GET .../owed`` for what a live booking stands at instead.
    """
    service = BookingService(db)
    booking = await service.get(booking_id)
    found = await service.settlement(booking_id)
    return CancellationSettlementRead(
        retained_amount=found.retained_amount,
        paid_amount=found.paid_amount,
        refund_due=found.refund_due,
        still_owed=found.still_owed,
        currency=booking.currency,
    )


@router.post("/bookings/{booking_id}/cancel", response_model=BookingRead)
async def cancel_booking(
    booking_id: uuid.UUID,
    body: CancelBooking,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(require_permission(MANAGE)),
):
    """Stop a booking, with the reason on the record and the ladder applied.

    See ``GET .../cancellation-preview`` to find out what this will retain
    before calling it — this endpoint commits to it.
    """
    return await BookingService(db).cancel(
        booking_id, reason=body.reason, actor_id=actor.id
    )


@router.post("/bookings/{booking_id}/complete", response_model=BookingRead)
async def complete_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(MANAGE)),
):
    """Mark a trip as travelled. Refused before the departure date."""
    return await BookingService(db).complete(booking_id)


@router.get("/bookings/{booking_id}/schedule", response_model=list[InstalmentRead])
async def booking_schedule(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(READ)),
):
    """The instalments as invoiced, in order.

    Frozen at the moment of booking: changing the deposit policy next month
    cannot restate an invoice already sent (§7.1).
    """
    booking = await BookingService(db).get(booking_id)
    return booking.instalments
