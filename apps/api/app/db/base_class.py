"""Declarative base and common column mixins.

Foundation rules enforced here:
- UUID v7 primary keys (time-ordered, safe to expose).
- Timestamps are timezone-aware (TIMESTAMPTZ), server-defaulted to UTC now().
- Whether a catalogue row is on the public website is a separate decision from
  whether it can be sold (see PublishableMixin).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.ids import uuid7


class Base(DeclarativeBase):
    """Declarative base for all models."""


class UUIDPKMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class PublishableMixin:
    """Whether this row is on the public website, and who put it there (§6.1).

    Kept apart from ``is_active`` on purpose, and here rather than in the
    public module because it is a property of the row rather than of the
    website. ``is_active`` means "the quote engine may price this", and it is
    set by whoever loads a rate sheet; a public site that read it would publish
    forty hotels the first time somebody imported a contract. Publishing is a
    person's decision, so it carries their id and the moment they made it.

    Defaults to **false**, including for every row that already exists: a
    migration that turned the catalogue public would be the single worst
    possible reading of this comment.
    """

    is_published: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_by: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
