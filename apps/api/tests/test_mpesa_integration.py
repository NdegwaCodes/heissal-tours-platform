"""The Daraja client's own pure arithmetic and parsing (§7.5).

No network, no config, no database — see ``test_mpesa_service.py`` and
``test_mpesa_router.py`` for the layers that need those. The sandbox
shortcode/passkey used below (174379 /
bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919) are
Safaricom's own published Daraja sandbox test credentials, used here only
because they are a fixed, publicly documented input — the expected output was
computed once by hand (base64 of their concatenation with a fixed timestamp),
not copied from a Safaricom example, so this checks the function's own
arithmetic rather than trusting a claimed source.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from app.integrations.mpesa import (
    MpesaError,
    normalise_phone,
    parse_stk_callback,
    stk_password,
    stk_timestamp,
    whole_kes,
)

D = Decimal


class TestNormalisePhone:
    def test_a_leading_zero_becomes_254(self):
        assert normalise_phone("0712345678") == "254712345678"

    def test_a_leading_zero_on_the_01_range_also_becomes_254(self):
        assert normalise_phone("0112345678") == "254112345678"

    def test_a_plus_254_number_is_accepted(self):
        assert normalise_phone("+254712345678") == "254712345678"

    def test_a_bare_254_number_is_accepted(self):
        assert normalise_phone("254712345678") == "254712345678"

    def test_spaces_throughout_are_stripped(self):
        assert normalise_phone("0712 345 678") == "254712345678"

    def test_a_nine_digit_number_with_no_prefix_at_all_is_accepted(self):
        assert normalise_phone("712345678") == "254712345678"

    def test_a_landline_style_number_is_refused(self):
        with pytest.raises(ValueError, match="does not look like"):
            normalise_phone("0203456789")

    def test_a_number_with_too_few_digits_is_refused(self):
        with pytest.raises(ValueError, match="does not look like"):
            normalise_phone("12345")


class TestStkPassword:
    def test_matches_a_hand_computed_value_for_the_daraja_sandbox_credentials(self):
        password = stk_password(
            shortcode="174379",
            passkey="bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
            timestamp="20160216165627",
        )
        assert password == (
            "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5"
            "YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMTYwMjE2MTY1NjI3"
        )

    def test_a_different_timestamp_changes_the_password(self):
        first = stk_password(shortcode="174379", passkey="secret", timestamp="20260101000000")
        second = stk_password(shortcode="174379", passkey="secret", timestamp="20260101000001")
        assert first != second


class TestStkTimestamp:
    def test_formats_to_the_second_with_no_separators(self):
        assert stk_timestamp(datetime(2026, 9, 13, 14, 49, 50)) == "20260913144950"


class TestWholeKes:
    def test_a_whole_amount_is_unchanged(self):
        assert whole_kes(D("5000")) == 5000

    def test_a_fraction_always_rounds_up(self):
        assert whole_kes(D("4999.01")) == 5000

    def test_a_fraction_just_under_the_next_shilling_still_rounds_up(self):
        assert whole_kes(D("4999.99")) == 5000


class TestParseStkCallback:
    def test_a_successful_callback_reads_every_metadata_field(self):
        payload = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "29115-34620561-1",
                    "CheckoutRequestID": "ws_CO_1234",
                    "ResultCode": 0,
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 15000},
                            {"Name": "MpesaReceiptNumber", "Value": "NLJ7RT61SV"},
                            {"Name": "TransactionDate", "Value": 20260913144950},
                            {"Name": "PhoneNumber", "Value": 254712345678},
                        ]
                    },
                }
            }
        }
        result = parse_stk_callback(payload)
        assert result.checkout_request_id == "ws_CO_1234"
        assert result.succeeded
        assert result.amount == D("15000")
        assert result.mpesa_receipt_number == "NLJ7RT61SV"
        assert result.transaction_date == "20260913144950"
        assert result.phone_number == "254712345678"

    def test_a_cancelled_prompt_has_no_metadata_and_is_not_a_success(self):
        payload = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "29115-34620561-1",
                    "CheckoutRequestID": "ws_CO_1234",
                    "ResultCode": 1032,
                    "ResultDesc": "Request cancelled by user.",
                }
            }
        }
        result = parse_stk_callback(payload)
        assert not result.succeeded
        assert result.amount is None
        assert result.mpesa_receipt_number is None

    def test_a_payload_with_no_stk_callback_body_is_refused(self):
        with pytest.raises(MpesaError, match="Not a recognisable"):
            parse_stk_callback({"unexpected": "shape"})

    def test_a_callback_missing_its_checkout_request_id_is_refused(self):
        payload = {"Body": {"stkCallback": {"ResultCode": 0, "ResultDesc": "ok"}}}
        with pytest.raises(MpesaError, match="no CheckoutRequestID"):
            parse_stk_callback(payload)
