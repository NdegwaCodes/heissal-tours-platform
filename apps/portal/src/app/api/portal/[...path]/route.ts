import { NextRequest, NextResponse } from "next/server";
import {
  API_BASE,
  API_V1,
  NO_LINK,
  READABLE,
  TOKEN_COOKIE,
  errorEnvelope,
} from "@/lib/session";

// The read proxy: /api/portal/<thing> -> /api/v1/portal/<thing>, with the
// grant token attached from the httpOnly cookie.
//
// Only GET is exported. That is not an oversight and it is not a policy
// either -- the 7.2 API has no write endpoint at all, so there is nothing for
// a POST here to forward. The absence of the handlers is the same guarantee
// the absence of the endpoints is.

async function handle(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  const { path } = await ctx.params;
  const target = path.join("/");

  // The allow-list. See READABLE.
  if (!(READABLE as readonly string[]).includes(target)) {
    return NextResponse.json(
      errorEnvelope("NOT_FOUND", "There is nothing to read there."),
      { status: 404 },
    );
  }

  const token = req.cookies.get(TOKEN_COOKIE)?.value;
  if (!token) {
    return NextResponse.json(NO_LINK, { status: 403 });
  }

  const apiRes = await fetch(`${API_BASE}${API_V1}/portal/${target}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  const text = await apiRes.text();
  const out = new NextResponse(text, {
    status: apiRes.status,
    headers: {
      // Passed through rather than assumed: document.html is HTML, and the
      // other two are JSON.
      "Content-Type":
        apiRes.headers.get("content-type") ?? "application/json",
      // Somebody else's holiday must never come out of a shared cache, and
      // the statement changes the moment a payment is recorded.
      "Cache-Control": "no-store, private",
    },
  });

  // A grant that has been revoked mid-session, or expired overnight in an
  // open tab: drop the cookie so the next page load shows the reason rather
  // than trying again with a credential that is gone.
  if (apiRes.status === 401 || apiRes.status === 403) {
    out.cookies.delete(TOKEN_COOKIE);
  }
  return out;
}

export { handle as GET };
