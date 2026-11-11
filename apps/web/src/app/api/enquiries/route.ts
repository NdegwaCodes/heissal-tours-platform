import { NextRequest, NextResponse } from "next/server";

// The enquiry form's one server-side hop.
//
// It exists so the browser does not address the API directly, and so the
// visitor's own address reaches the API's rate limiter rather than this
// server's. Everything else -- what is required, what is refused, the trap
// field, becoming a lead and an inbound log entry -- is the API's job, and the
// message it refuses with is written to be read by whoever filled the form.
// This handler adds no validation of its own on purpose: a second set of rules
// here would be a second thing to keep in step, and the one that drifted would
// be the one telling a customer their email address is wrong when it is not.

const API_BASE = process.env.API_BASE_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const body = await req.text();

  // So the API's limiter counts the visitor rather than this server, which
  // would otherwise be the one caller sending every enquiry on the site. It
  // is only honoured where the API's own deployment says to trust a proxy --
  // see app/core/limits.py on why the header is not trusted by default.
  const forwarded = req.headers.get("x-forwarded-for");

  const upstream = await fetch(`${API_BASE}/api/v1/public/enquiries`, {
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
