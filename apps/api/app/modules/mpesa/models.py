"""One row per STK push, from the moment it is sent until it settles (§7.5).

Why this exists at all rather than creating a ``Payment`` directly from a
callback: the callback's only handle on the world is a ``CheckoutRequestID``
Safaricom minted when the push was sent, and something has to remember which
booking, which instalment and which phone number that ID belongs to. This
table is that memory, and it exists from the moment the push is *sent* — a
customer who never enters their PIN, or enters it wrong, leaves a row here
that says so, which is the difference between "we don't know what happened"
and "we asked, and here is what Safaricom said back."
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDPKMixin

#: Sent, awaiting the callback (or a status query).
PENDING = "pending"
#: ResultCode 0 — a Payment row exists and payment_id is set.
COMPLETED = "completed"
#: A non-zero ResultCode — the customer cancelled, entered the wrong PIN,
#: the request timed out, or similar. Not an error in this system; an
#: ordinary outcome an operator needs to see.
FAILED = "failed"
MPESA_TRANSACTION_STATUSES = (PENDING, COMPLETED, FAILED)


class MpesaTransaction(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "mpesa_transactions"
    __table_args__ = (
        CheckConstraint(
            "status in ('pending', 'completed', 'failed')",
            name="ck_mpesa_transaction_status",
        ),
        CheckConstraint("amount > 0", name="ck_mpesa_transaction_amount_positive"),
        Index("ix_mpesa_transaction_booking", "booking_id"),
    )

    booking_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
    )
    #: Which instalment this push was for, where the caller named one. Not
    #: required — an agent can push an arbitrary amount against a booking
    #: the same way a manually recorded payment can (§7.1).
    instalment_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("booking_instalments.id", ondelete="SET NULL"),
        nullable=True,
    )
    #: Set once the callback (or a status query) reports success — the same
    #: row ``GET /bookings/{id}/owed`` already reads, not a parallel figure.
    payment_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
    )
    #: 2547XXXXXXXX — normalised on the way in (app.integrations.mpesa.
    #: normalise_phone), never the raw string a form happened to submit.
    phone_number: Mapped[str] = mapped_column(String(12), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=PENDING, index=True, nullable=False
    )
    merchant_request_id: Mapped[str] = mapped_column(String(60), nullable=False)
    #: Safaricom's own correlation key. Unique because it is exactly that — a
    #: second callback for one already resolves to the same row rather than
    #: creating a second (Safaricom's own docs note callbacks can repeat).
    checkout_request_id: Mapped[str] = mapped_column(
        String(60), unique=True, index=True, nullable=False
    )
    result_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result_desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    mpesa_receipt_number: Mapped[str | None] = mapped_column(
        String(30), index=True, nullable=True
    )
    callback_received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    initiated_by: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    booking = relationship("Booking")
    payment = relationship("Payment")


__all__ = [
    "COMPLETED",
    "FAILED",
    "MPESA_TRANSACTION_STATUSES",
    "PENDING",
    "MpesaTransaction",
]
