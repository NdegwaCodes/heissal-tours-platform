"""The Safaricom Daraja client — STK push, and the arithmetic behind it (§7.5).

Unlike every other seam in this package (:mod:`narrative`, :mod:`pdf_render`,
:mod:`rate_extraction`), this is not "no provider is chosen yet." The client
picked direct M-Pesa integration on 2026-09-13, with a developer account and a
paybill/till number already in hand — so this is a real client against a real
API, not a protocol waiting for one. What still does not ship is the
**secret**: ``MPESA_CONSUMER_KEY``, ``MPESA_CONSUMER_SECRET``, ``MPESA_
SHORTCODE`` and ``MPESA_PASSKEY`` are blank by default, :meth:`MpesaClient.
is_configured` refuses out loud rather than sending a request with an empty
key, and filling those four values in is the one remaining step.

**Two calls, and they answer two different questions.** ``initiate_stk_push``
asks a customer's phone to prompt them for a PIN — Safaricom's own name for
this is "Lipa na M-Pesa Online" — and returns immediately with a
``CheckoutRequestID``, not a result: whether the customer actually paid comes
later, either as a callback to our own server or by asking again with
``query_stk_push``. Treating the initiate call's own success as "the customer
has paid" is the single most common M-Pesa integration mistake, and this
client's return type (``StkPushAccepted``, not a payment) is written so that
mistake is not the easy path.

**The password is derived, not stored.** Daraja's own scheme —
base64(shortcode + passkey + timestamp) — means the passkey never travels on
its own; :func:`stk_password` is pure and tested against a hand-computed
expected value, so a transposed character in a config value shows up as a
test failure rather than a live rejection during a demo.

**Amounts are whole numbers.** Daraja rejects a decimal amount outright, and
this business's money is exact to the cent everywhere else in the system
(§2's own rule) — so rounding happens once, here, at the boundary where a
Decimal has to become an integer for a vendor's API, and the rounding
direction is up: a customer is never asked to pay less than what is actually
owed because of how a fraction was dropped.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_CEILING, Decimal
from typing import Any

import httpx

from app.core.config import settings

SANDBOX_BASE_URL = "https://sandbox.safaricom.co.ke"
PRODUCTION_BASE_URL = "https://api.safaricom.co.ke"

PAYBILL = "paybill"
TILL = "till"
#: Daraja's own names for the two shapes of transaction.
_TRANSACTION_TYPES = {
    PAYBILL: "CustomerPayBillOnline",
    TILL: "CustomerBuyGoodsOnline",
}

#: Daraja's own timestamp format, to the second, used both in the STK
#: password and as the request's own Timestamp field.
TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"


class MpesaUnavailable(RuntimeError):
    """Not configured — see the four required settings named in the message."""


class MpesaError(RuntimeError):
    """Daraja was reached and refused the request, with its own explanation.

    Distinct from :class:`MpesaUnavailable`: this means the credentials work
    and Safaricom's own API rejected something about the request itself (a
    malformed phone number, an amount below their minimum, a shortcode that
    does not support STK push) — worth surfacing differently to an operator,
    the same distinction :mod:`pdf_render` draws between a missing renderer
    and a broken one.
    """


def normalise_phone(value: str) -> str:
    """A Kenyan mobile number in the one shape Daraja accepts: ``2547XXXXXXXX``.

    Kenyans write a number four different ways in a booking form — with a
    leading 0, a leading +254, a leading 254, or with spaces throughout — and
    Daraja accepts exactly one of them. Normalised here, once, rather than
    trusting whoever last typed it into a phone field.
    """
    digits = "".join(ch for ch in value if ch.isdigit())
    if digits.startswith("0") and len(digits) == 10:
        digits = "254" + digits[1:]
    elif digits.startswith("254") and len(digits) == 12:
        pass
    elif len(digits) == 9:
        digits = "254" + digits

    # Safaricom and other Kenyan mobile numbers run 2547XXXXXXXX; the newer
    # 01-prefixed range (introduced ~2019, mostly Safaricom) runs 2541XXXXXXXX.
    # Written as an explicit boolean rather than relying on operator
    # precedence between `or`/`and`/`not` to read correctly.
    right_length = len(digits) == 12
    right_prefix = digits.startswith("2547") or digits.startswith("2541")
    if not (right_length and right_prefix):
        raise ValueError(
            f"'{value}' does not look like a Kenyan mobile number. Expected "
            f"something like 0712345678 or +254712345678."
        )
    return digits


def stk_timestamp(now: datetime) -> str:
    return now.strftime(TIMESTAMP_FORMAT)


def stk_password(*, shortcode: str, passkey: str, timestamp: str) -> str:
    """base64(shortcode + passkey + timestamp) — Daraja's own scheme.

    Pure and given its own tests against a hand-computed expected value —
    the whole function is base64 of a concatenation, so "correct" is
    something a test can check exactly, and a transposed character in a
    config value fails a test in under a second rather than failing
    silently against the sandbox.
    """
    raw = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(raw.encode("ascii")).decode("ascii")


def whole_kes(amount: Decimal) -> int:
    """Round up to the nearest shilling — Daraja takes no decimal places.

    Upward, not to the nearest: a customer asked to pay less than what is
    owed because a fraction of a shilling was dropped is a shortfall this
    system would then have to notice and chase separately. Rounding down
    would save a customer a few cents in a way nobody asked for and cost the
    business the same few cents on every single transaction.
    """
    return int(amount.quantize(Decimal("1"), rounding=ROUND_CEILING))


@dataclass(frozen=True)
class StkPushAccepted:
    """Safaricom has queued the prompt. Not a payment — see the module
    docstring on why this type is not called ``Payment``."""

    merchant_request_id: str
    checkout_request_id: str
    customer_message: str


@dataclass(frozen=True)
class StkPushResult:
    """What actually happened, from a callback or a status query.

    ``result_code == 0`` is Safaricom's own success code; everything else is
    a reason, not an error this client raises — a customer entering the
    wrong PIN or cancelling the prompt is an ordinary outcome an operator
    needs to see, not an exception to catch.
    """

    checkout_request_id: str
    result_code: int
    result_desc: str
    amount: Decimal | None = None
    mpesa_receipt_number: str | None = None
    transaction_date: str | None = None
    phone_number: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.result_code == 0


class MpesaClient:
    """A thin wrapper over the two Daraja calls this integration needs.

    Holds no state across requests beyond a cached OAuth token — everything
    else (which transaction a callback belongs to, whether a payment has
    already been recorded for it) lives in the database, in
    :mod:`app.modules.mpesa.service`, because a client library restarted
    between a push and its callback must not lose track of either.
    """

    def __init__(
        self,
        *,
        environment: str,
        consumer_key: str | None,
        consumer_secret: str | None,
        shortcode: str | None,
        shortcode_type: str,
        passkey: str | None,
        callback_url: str | None,
        token_cache_seconds: int = 3500,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = PRODUCTION_BASE_URL if environment == "production" else SANDBOX_BASE_URL
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.shortcode = shortcode
        self.shortcode_type = shortcode_type
        self.passkey = passkey
        self.callback_url = callback_url
        self.token_cache_seconds = token_cache_seconds
        self._client = client or httpx.AsyncClient(timeout=30.0)
        self._token: str | None = None
        self._token_expires_at: datetime | None = None

    @property
    def is_configured(self) -> bool:
        return bool(
            self.consumer_key
            and self.consumer_secret
            and self.shortcode
            and self.passkey
            and self.callback_url
        )

    def _require_configured(self) -> None:
        if self.is_configured:
            return
        missing = [
            name
            for name, value in (
                ("MPESA_CONSUMER_KEY", self.consumer_key),
                ("MPESA_CONSUMER_SECRET", self.consumer_secret),
                ("MPESA_SHORTCODE", self.shortcode),
                ("MPESA_PASSKEY", self.passkey),
                ("MPESA_CALLBACK_BASE_URL", self.callback_url),
            )
            if not value
        ]
        raise MpesaUnavailable(
            f"M-Pesa is not configured — missing {', '.join(missing)}. The "
            f"integration is built; these are the only values left to add."
        )

    async def _access_token(self, *, now: datetime) -> str:
        if self._token and self._token_expires_at and now < self._token_expires_at:
            return self._token
        resp = await self._client.get(
            f"{self.base_url}/oauth/v1/generate",
            params={"grant_type": "client_credentials"},
            auth=(self.consumer_key or "", self.consumer_secret or ""),
        )
        if resp.status_code != 200:
            raise MpesaError(
                f"Daraja refused to issue an access token ({resp.status_code}): "
                f"{resp.text[:300]}"
            )
        body = resp.json()
        token = body.get("access_token")
        if not token:
            raise MpesaError(f"Daraja's token response had no access_token: {body}")
        self._token = token
        # A little short of what Daraja actually grants, so a token already
        # near its own expiry is never handed to a request that would arrive
        # after it lapses.
        self._token_expires_at = now + timedelta(seconds=self.token_cache_seconds)
        return token

    async def initiate_stk_push(
        self,
        *,
        phone_number: str,
        amount: Decimal,
        account_reference: str,
        description: str,
        now: datetime,
    ) -> StkPushAccepted:
        """Ask a customer's phone to prompt them for their M-Pesa PIN.

        Returns as soon as Safaricom has *queued* the prompt — see the module
        docstring on why that is not the same thing as a payment.
        """
        self._require_configured()
        phone = normalise_phone(phone_number)
        timestamp = stk_timestamp(now)
        password = stk_password(
            shortcode=self.shortcode or "", passkey=self.passkey or "", timestamp=timestamp
        )
        token = await self._access_token(now=now)

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": _TRANSACTION_TYPES[self.shortcode_type],
            "Amount": whole_kes(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.callback_url,
            # Daraja truncates silently past 12 characters — cut here so the
            # value on the customer's own prompt matches what was sent.
            "AccountReference": account_reference[:12],
            "TransactionDesc": description[:13] or "Payment",
        }
        resp = await self._client.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        body: dict[str, Any] = resp.json() if resp.content else {}
        if resp.status_code != 200 or body.get("ResponseCode") not in ("0", 0):
            raise MpesaError(
                f"Daraja refused the STK push ({resp.status_code}): "
                f"{body.get('errorMessage') or body.get('ResponseDescription') or resp.text[:300]}"
            )
        return StkPushAccepted(
            merchant_request_id=str(body["MerchantRequestID"]),
            checkout_request_id=str(body["CheckoutRequestID"]),
            customer_message=str(body.get("CustomerMessage") or ""),
        )

    async def query_stk_push(
        self, *, checkout_request_id: str, now: datetime
    ) -> StkPushResult:
        """Ask Daraja directly, for when a callback never arrived.

        Safaricom's own documentation recommends this as the fallback: a
        callback is a single HTTP request from their side to ours, and one
        that does not arrive — a firewall, a deploy mid-flight, a transient
        network fault — should not mean a payment is invisible forever.
        """
        self._require_configured()
        timestamp = stk_timestamp(now)
        password = stk_password(
            shortcode=self.shortcode or "", passkey=self.passkey or "", timestamp=timestamp
        )
        token = await self._access_token(now=now)
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id,
        }
        resp = await self._client.post(
            f"{self.base_url}/mpesa/stkpushquery/v1/query",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        body: dict[str, Any] = resp.json() if resp.content else {}
        # A still-pending push answers with ResultCode 1032/"still being
        # processed"-style codes, which is a real, ordinary state — not
        # every non-zero code here means "failed", only that a client of
        # this method must not assume 0 the way it must not assume success.
        code = body.get("ResultCode")
        if code is None:
            raise MpesaError(f"Daraja's status query had no ResultCode: {body}")
        return StkPushResult(
            checkout_request_id=checkout_request_id,
            result_code=int(code),
            result_desc=str(body.get("ResultDesc") or ""),
        )

    async def aclose(self) -> None:
        await self._client.aclose()


def parse_stk_callback(payload: dict[str, Any]) -> StkPushResult:
    """Daraja's own callback shape, read into :class:`StkPushResult`.

    A successful callback carries its facts in ``CallbackMetadata.Item`` as a
    list of ``{"Name": ..., "Value": ...}`` pairs rather than a flat object —
    Safaricom's own choice, not this codebase's — so this is the one place
    that shape is ever read.
    """
    try:
        body = payload["Body"]["stkCallback"]
    except (KeyError, TypeError) as exc:
        raise MpesaError(f"Not a recognisable STK callback: {payload}") from exc

    checkout_request_id = str(body.get("CheckoutRequestID") or "")
    result_code = int(body.get("ResultCode", -1))
    result_desc = str(body.get("ResultDesc") or "")
    if not checkout_request_id:
        raise MpesaError(f"Callback had no CheckoutRequestID: {payload}")

    items = {}
    metadata = body.get("CallbackMetadata") or {}
    for item in metadata.get("Item", []):
        name = item.get("Name")
        if name:
            items[name] = item.get("Value")

    amount = items.get("Amount")
    return StkPushResult(
        checkout_request_id=checkout_request_id,
        result_code=result_code,
        result_desc=result_desc,
        amount=Decimal(str(amount)) if amount is not None else None,
        mpesa_receipt_number=(
            str(items["MpesaReceiptNumber"]) if "MpesaReceiptNumber" in items else None
        ),
        transaction_date=(
            str(items["TransactionDate"]) if "TransactionDate" in items else None
        ),
        phone_number=(str(items["PhoneNumber"]) if "PhoneNumber" in items else None),
    )


# A module-level singleton, built once from settings, the same pattern
# app.core.redis uses — so the cached OAuth token actually survives between
# requests instead of being re-fetched on every single push.
mpesa_client = MpesaClient(
    environment=settings.MPESA_ENVIRONMENT,
    consumer_key=settings.MPESA_CONSUMER_KEY,
    consumer_secret=settings.MPESA_CONSUMER_SECRET,
    shortcode=settings.MPESA_SHORTCODE,
    shortcode_type=settings.MPESA_SHORTCODE_TYPE,
    passkey=settings.MPESA_PASSKEY,
    callback_url=settings.MPESA_CALLBACK_BASE_URL,
    token_cache_seconds=settings.MPESA_TOKEN_CACHE_SECONDS,
)


async def get_mpesa_client() -> MpesaClient:
    return mpesa_client


__all__ = [
    "PAYBILL",
    "PRODUCTION_BASE_URL",
    "SANDBOX_BASE_URL",
    "TILL",
    "MpesaClient",
    "MpesaError",
    "MpesaUnavailable",
    "StkPushAccepted",
    "StkPushResult",
    "get_mpesa_client",
    "mpesa_client",
    "normalise_phone",
    "parse_stk_callback",
    "stk_password",
    "stk_timestamp",
    "whole_kes",
]
