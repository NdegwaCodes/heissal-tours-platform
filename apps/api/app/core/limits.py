"""Rate limiting, which ``redis.py``'s own docstring has been promising.

Nothing in this platform has ever needed it. Every route until now sat behind
a login, and a member of staff hammering the quote engine is a conversation
rather than a control. §6.1 opens the first endpoints to the entire internet,
including one that **writes** — and a lead form with no limiter on it is a
pipeline that fills with rubbish the first week somebody points a script at
it.

A fixed window, deliberately, rather than a token bucket or a sliding log. It
is two Redis commands, it is obvious when read six months from now, and its
one flaw — a caller can spend a whole window's allowance at the boundary and
another immediately after — matters for a login endpoint and does not matter
for "five enquiries an hour".

**It fails open.** If Redis is unreachable the request is allowed and a
warning is logged. That is the right way round for what is behind these
limits: a lost enquiry is a customer who telephoned a competitor instead,
while an extra spam row is something somebody deletes in a second. A limiter
that took the website's contact form down because a cache restarted would be
the more expensive failure by a wide margin.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from fastapi import Depends, Request

from app.core.errors import AppError
from app.core.redis import redis_client

logger = logging.getLogger("heissal.limits")


class TooManyRequests(AppError):
    """Over the limit. 429, with how long to wait."""

    status_code = 429
    code = "RATE_LIMITED"


@dataclass(frozen=True)
class Window:
    """How many, over how long."""

    limit: int
    seconds: int

    def __post_init__(self) -> None:
        if self.limit < 1 or self.seconds < 1:
            raise ValueError("A window needs a positive limit and duration.")


def caller(request: Request) -> str:
    """Who is asking, as well as this can be known.

    The socket address, and **not** ``X-Forwarded-For``: that header is
    attacker-controlled unless a proxy we trust has overwritten it, and a
    limiter keyed on a value the caller chooses is not a limiter. When this
    runs behind a load balancer the deployment has to tell Uvicorn to trust
    it (``--proxy-headers`` with ``--forwarded-allow-ips``), which puts the
    decision where the trust actually lives.
    """
    return request.client.host if request.client else "unknown"


async def spend(key: str, window: Window) -> int:
    """Count one request against ``key``. Returns the count so far.

    Raises :class:`TooManyRequests` when the window is used up. The expiry is
    set only on the first request of a window, so a caller cannot keep the
    window alive by continuing to hammer it.
    """
    try:
        count = int(await redis_client.incr(key))
        if count == 1:
            await redis_client.expire(key, window.seconds)
        ttl = int(await redis_client.ttl(key))
    except Exception:  # noqa: BLE001 - see the module docstring on failing open
        logger.warning("Rate limiter unavailable; allowing %s", key, exc_info=True)
        return 0

    if count > window.limit:
        wait = max(ttl, 1)
        raise TooManyRequests(
            f"Too many requests. Please try again in {wait} second(s)."
        )
    return count


def rate_limit(
    *, bucket: str, limit: int, seconds: int
) -> Callable[..., Awaitable[None]]:
    """A dependency that limits ``bucket`` to ``limit`` per ``seconds``, per caller.

    ``bucket`` names the thing being protected rather than the route, so two
    routes that should share an allowance can, and a route that is renamed
    does not silently reset everybody's count.
    """
    window = Window(limit=limit, seconds=seconds)

    async def _guard(who: str = Depends(caller)) -> None:
        await spend(f"ratelimit:{bucket}:{who}", window)

    return _guard


__all__ = ["TooManyRequests", "Window", "caller", "rate_limit", "spend"]
