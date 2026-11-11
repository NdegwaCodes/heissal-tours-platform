"""``GET /public/contact`` — the same source the quotation document prints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.core.config import settings
from tests.conftest import auth_headers

pytestmark = pytest.mark.asyncio(loop_scope="session")

V1 = settings.API_V1_STR


async def test_contact_needs_no_login_and_matches_document_config(
    client: AsyncClient, admin_tokens: dict
):
    headers = auth_headers(admin_tokens)
    doc = (await client.get(f"{V1}/document-config", headers=headers)).json()

    resp = await client.get(f"{V1}/public/contact")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["company_name"] == doc["company_name"]
    assert body["contact_email"] == doc["contact_email"]
    assert body["contact_phone"] == doc["contact_phone"]
    assert body["social_line"] == doc["social_line"]
    # An allow-list, not the whole config: brand colours, the why-us list and
    # the tagline lines are not the website's business.
    assert "why_us_points" not in body
