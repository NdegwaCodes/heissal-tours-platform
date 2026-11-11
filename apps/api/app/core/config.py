"""Application configuration, loaded from environment / .env.

All secrets and environment-specific values come from the environment. Nothing
business-related is hard-coded here — this is infrastructure configuration only.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # pydantic-settings gives LATER files priority, so the repo-root .env is
        # the shared fallback and the app-local apps/api/.env wins over it. The
        # reverse order silently ignored a local override — which pointed a test
        # run at the hosted production DB. Real environment variables still beat
        # both, which is how CI and the throwaway-test DB override this.
        env_file=("../../.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- General ---
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Heissal Tours & Travel Platform"
    TIMEZONE: str = "Africa/Nairobi"
    BASE_REPORTING_CURRENCY: str = "USD"

    # --- API ---
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(default_factory=list)

    # --- Database ---
    POSTGRES_USER: str = "heissal"
    POSTGRES_PASSWORD: str = "heissal"
    POSTGRES_DB: str = "heissal"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Security ---
    JWT_SECRET_KEY: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # --- Client portal (Stage 7.2) ---
    # Where a client's own trip lives. The base of the link an agent sends;
    # the access token goes in the URL **fragment**, which browsers never send
    # to a server, so it stays out of access logs and Referer headers.
    PORTAL_BASE_URL: str = "http://localhost:3001"
    # How long after they travel a client can still open their trip. Not
    # arbitrary and not "until departure": receipts, the statement and the
    # itinerary are all wanted after the fact, and a link that dies on the day
    # they fly home is a support call.
    PORTAL_ACCESS_DAYS_AFTER_TRAVEL: int = 90

    # --- M-Pesa / Safaricom Daraja (Stage 7.5, client-chosen 2026-09-13) ---
    # Direct integration, not an aggregator — the client's own choice, made
    # with a developer account and a paybill/till number already in hand.
    # Every value below is blank by default: `MpesaClient.is_configured`
    # refuses out loud rather than sending a request with an empty consumer
    # key, the same seam convention as every other provider in
    # app/integrations/ (see narrative.py, pdf_render.py). Filling these in
    # is the one remaining step — nothing else about the integration waits
    # on it.
    MPESA_ENVIRONMENT: str = "sandbox"  # "sandbox" or "production"
    MPESA_CONSUMER_KEY: str | None = None
    MPESA_CONSUMER_SECRET: str | None = None
    # The paybill (CustomerPayBillOnline) or till (CustomerBuyGoodsOnline)
    # number STK push charges against.
    MPESA_SHORTCODE: str | None = None
    MPESA_SHORTCODE_TYPE: str = "paybill"  # "paybill" or "till"
    # Issued by Safaricom alongside the shortcode; used only to build the STK
    # push password, never sent over the wire on its own.
    MPESA_PASSKEY: str | None = None
    # Where Safaricom calls back with the result. Must be a public HTTPS URL
    # Safaricom can reach — a local machine behind NAT cannot receive this,
    # which is what the sandbox's own docs mean by "publicly accessible".
    MPESA_CALLBACK_BASE_URL: str | None = None
    # How long an OAuth access token is cached for before it is re-requested.
    # Daraja itself says ~3600s; kept a little short of that so a token is
    # never used past the edge of its own expiry.
    MPESA_TOKEN_CACHE_SECONDS: int = 3500
    # Optional hardening: Safaricom's published callback IP ranges, comma-
    # separated. Empty means no restriction — sandbox testing has no fixed
    # range to check against, and the real check a callback has to pass is
    # that its CheckoutRequestID matches a transaction this system actually
    # initiated, which needs no IP list at all.
    MPESA_CALLBACK_ALLOWED_IPS: str = ""

    # --- Public website (Stage 6.1) ---
    # The first endpoints in this platform open to the whole internet, so both
    # of these are limits rather than niceties. Per caller, fixed window.
    #
    # Reads are generous: a single page of a website makes several calls and a
    # family browsing on one office connection shares an address. It is a
    # ceiling on a script, not on a visitor.
    PUBLIC_READ_PER_MINUTE: int = 120
    # Enquiries are not. Nobody sends the same business six genuine enquiries
    # in an hour, and the form is the only place a stranger can write.
    PUBLIC_ENQUIRIES_PER_HOUR: int = 5
    # An estimate (§6.3) computes rather than writes, but each call is several
    # queries and a build-up, not one row lookup — tighter than a plain read
    # for that reason, generous enough that trying every comfort level on a
    # multi-leg trip is not throttled mid-session.
    PUBLIC_ESTIMATES_PER_HOUR: int = 60

    # --- First superuser (seed) ---
    FIRST_SUPERUSER_EMAIL: str = "admin@heissal.co.ke"
    FIRST_SUPERUSER_PASSWORD: str = "ChangeMe123!"
    FIRST_SUPERUSER_NAME: str = "Platform Admin"

    # --- Uploaded files (supplier rate sheets, property images) ---
    # Bytes live on the filesystem, not in Postgres (see the decision log): a
    # 10 MB scanned contract in a row makes every query that touches the table
    # pay for it. Relative paths are resolved against the API app directory so a
    # default deployment needs no configuration.
    UPLOAD_ROOT: str = "var/uploads"
    MAX_UPLOAD_BYTES: int = 25 * 1024 * 1024

    # --- PDF rendering (Stage 3.6) ---
    # The quotation is printed through a headless Chromium-family browser,
    # because the template was designed and visually verified in one: CSS grid,
    # object-fit and @page all behave as intended. Left empty, the renderer looks
    # in the usual places for each platform, so a normal developer machine and a
    # normal container both work unconfigured. Set it to pin a specific browser —
    # different engines paginate differently, and a client proposal should not
    # change shape because a host had a different browser installed.
    PDF_BROWSER_PATH: str | None = None
    # Required in most containers, where Chromium cannot use its sandbox. Off by
    # default because it is a real reduction in isolation and only the deployment
    # knows whether it is needed.
    PDF_BROWSER_NO_SANDBOX: bool = False
    # A ceiling on how long layout may settle before the snapshot, not a wait:
    # the document carries no scripts.
    PDF_RENDER_SETTLE_MS: int = 3000
    PDF_RENDER_TIMEOUT_SECONDS: int = 60
    # A stopgap for one specific CI runner where headless Chromium's
    # print-to-pdf step hangs indefinitely even with its sandbox restriction
    # lifted -- see tests/test_document_pdf.py's ci_pdf_hang marker and
    # .github/workflows/ci.yml. Off everywhere except that one workflow.
    PDF_TESTS_KNOWN_TO_HANG: bool = False

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    # libpq/psycopg2 connection params that asyncpg does not understand and must
    # be stripped from the async URL (SSL is passed via connect_args instead).
    _LIBPQ_ONLY_QUERY_KEYS = frozenset(
        {"sslmode", "channel_binding", "sslrootcert", "sslcert", "sslkey", "options"}
    )

    def _raw_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def _url_with_driver(self, driver: str, *, strip_libpq: bool) -> str:
        from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

        parts = urlsplit(self._raw_database_url())
        scheme = f"postgresql+{driver}"
        query = parts.query
        if strip_libpq and query:
            kept = [
                (k, v)
                for k, v in parse_qsl(query, keep_blank_values=True)
                if k not in self._LIBPQ_ONLY_QUERY_KEYS
            ]
            query = urlencode(kept)
        return urlunsplit((scheme, parts.netloc, parts.path, query, parts.fragment))

    @property
    def sqlalchemy_database_uri(self) -> str:
        """Async SQLAlchemy URL (asyncpg). libpq-only params are stripped; SSL for
        those is applied via :attr:`async_connect_args`."""
        return self._url_with_driver("asyncpg", strip_libpq=True)

    @property
    def sqlalchemy_sync_uri(self) -> str:
        """Sync SQLAlchemy URL (psycopg2) for Alembic — libpq params kept as-is."""
        return self._url_with_driver("psycopg2", strip_libpq=False)

    def _db_sslmode(self) -> str | None:
        from urllib.parse import parse_qsl, urlsplit

        query = urlsplit(self._raw_database_url()).query
        for key, value in parse_qsl(query, keep_blank_values=True):
            if key == "sslmode":
                return value.lower()
        return None

    @property
    def async_connect_args(self) -> dict[str, object]:
        """asyncpg connect args derived from the URL — SSL and pooler safety.

        - ``sslmode`` (a libpq param asyncpg can't read from the URL) becomes an
          asyncpg ``ssl`` value, so hosted Postgres like Neon connects over TLS.
        - Poolers (PgBouncer transaction mode, e.g. Neon's ``-pooler`` host)
          break asyncpg's prepared-statement cache, so it is disabled there.
        """
        args: dict[str, object] = {}
        sslmode = self._db_sslmode()
        if sslmode in {"require", "verify-ca", "verify-full", "prefer", "allow"}:
            args["ssl"] = sslmode
        elif sslmode == "disable":
            args["ssl"] = False

        host = self._raw_database_url()
        if "neon.tech" in host or "pooler" in host:
            args["statement_cache_size"] = 0
        return args

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
