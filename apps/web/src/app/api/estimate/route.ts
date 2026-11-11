import { NextRequest, NextResponse } from "next/server";

// The safari builder's one server-side hop, mirroring api/enquiries/route.ts.
//
// The browser never addresses the API (see next.config.mjs and the API's own
// public router on why), and forwarding X-Forwarded-For here is what lets the
// API's rate limiter count the visitor building a trip rather than this
// server, which would otherwise look like one caller pricing every visit to
// the site. This handler validates nothing of its own: the legs, the tiers
// and the party shape are the API's rules (app/modules/public/estimate.py),
// and a refusal it writes is meant to be read by the visitor who triggered it.

const API_BASE = process.env.API_BASE_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const body = await req.text();
  const forwarded = req.headers.get("x-forwarded-for");

  const upstream = await fetch(`${API_BASE}/api/v1/public/estimate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(forwarded ? { "X-Forwarded-For": forwarded } : {}),
    },
    body,
    cache: "no-store",
  });

  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: {
      "Content-Type":
        upstream.headers.get("content-type") ?? "application/json",
      "Cache-Control": "no-store",
    },
  });
}
