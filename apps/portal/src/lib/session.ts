// The one piece of machinery this app adds to the 7.2 API: turning the token
// out of the link's fragment into a session.
//
// The fragment keeps the token out of every server's logs while the *link* is
// travelling -- through WhatsApp, an email gateway, a link-preview fetcher,
// the Referer header of whatever the client clicks next. That is what it is
// for, and it is worth having. But a fragment is readable by any script on
// the page, and it sits in the address bar and in the history entry, so once
// the client has actually opened their trip the fragment is the wrong place
// to keep it.
//
// So the app lifts it out once, hands it to its own server, and keeps it in
// an httpOnly cookie:
//
//   * out of the address bar (history.replaceState drops the hash), so a
//     screenshot of the itinerary is not a working link;
//   * out of reach of page JavaScript, so an injected script cannot read it;
//   * confined to this origin, so it goes nowhere the API is not.
//
// It is deliberately NOT a login. There is no account, nothing to reset, and
// the cookie is worth exactly one trip for a few hours.

export const TOKEN_COOKIE = "heissal_trip";

// Read at request time, not build time (see next.config.mjs). This module is
// imported only by the two route handlers, so it stays on the server.
export const API_BASE = process.env.API_BASE_URL ?? "http://localhost:8000";
export const API_V1 = "/api/v1";

// Short, because the link is the credential and it is always to hand: a
// client who comes back next week clicks the link again. Long enough that
// reading the itinerary, the statement and the proposal in one sitting -- and
// coming back after lunch -- does not ask them to.
export const TOKEN_MAX_AGE = 60 * 60 * 12; // 12 hours

export const cookieOptions = () => ({
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  // strict, not lax: nothing outside this app ever needs to navigate *into*
  // it carrying the cookie. The arrival from WhatsApp does not need it -- the
  // token is in the fragment on that hop, which is the whole design.
  sameSite: "strict" as const,
  path: "/",
  maxAge: TOKEN_MAX_AGE,
});

// The three things a client may read, named here as well as in the API.
//
// The API would refuse anything else anyway -- a grant is not a user, and no
// guard in the system accepts one. This list is the same allow-list argument
// the view model makes (7.2): a proxy that forwarded whatever it was handed
// is one future endpoint away from forwarding something it should not, and
// that endpoint is always added by somebody who has never read this file.
export const READABLE = ["trip", "statement", "document.html"] as const;

export const errorEnvelope = (code: string, message: string) => ({
  error: { code, message, details: [] as unknown[] },
});

// What to say when there is no cookie and no token. Not "please sign in":
// there is nothing to sign in to, and advice a client cannot follow is worse
// than none.
export const NO_LINK = errorEnvelope(
  "portal_no_link",
  "Open your trip using the link your consultant sent you.",
);
