import { NextRequest, NextResponse } from "next/server";
import {
  API_BASE,
  API_V1,
  NO_LINK,
  TOKEN_COOKIE,
  cookieOptions,
} from "@/lib/session";

// Exchange the token out of the link's fragment for an httpOnly cookie.
// See src/lib/session.ts for why the fragment is right for the link and wrong
// for the session.
//
// The token is validated by asking the API for the trip, which is the only
// honest way to validate it: this app holds no hashes and knows nothing about
// grants. The trip comes back in this response too, so a client who has just
// clicked their link waits for one round trip rather than two.

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  const token = typeof body?.token === "string" ? body.token.trim() : "";

  if (!token) {
    return NextResponse.json(NO_LINK, { status: 403 });
  }

  const res = await fetch(`${API_BASE}${API_V1}/portal/trip`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  // A dead link is passed through exactly as the API refused it -- expired,
  // withdrawn, or a cancelled booking, each with its own sentence (7.2). No
  // cookie is set, so a bad token cannot be retried silently on the next
  // page load either.
  if (!res.ok) {
    const out = NextResponse.json(data ?? NO_LINK, { status: res.status });
    out.cookies.delete(TOKEN_COOKIE);
    return out;
  }

  const out = NextResponse.json(data);
  out.cookies.set(TOKEN_COOKIE, token, cookieOptions());
  return out;
}

// Leaving. Worth having because this is the one page in the platform that
// gets opened on a hotel's business-centre computer: it drops the cookie so
// the next person to sit down has a dead tab rather than somebody's
// itinerary. It writes nothing to the API -- the grant stays live, and the
// client's own link still works.
export async function DELETE() {
  const out = NextResponse.json({ ok: true });
  out.cookies.delete(TOKEN_COOKIE);
  return out;
}
