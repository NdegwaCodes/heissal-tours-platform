import { NextRequest, NextResponse } from "next/server";

// Photographs, proxied.
//
// The API serves these from /api/v1/public/images/<kind>/<id> and checks that
// whatever the photograph belongs to is actually published before handing it
// over. Going through this app keeps that one rule in one place while still
// meaning the browser talks only to this origin -- which is what lets the API
// ship with no CORS configuration at all.
//
// The rows are immutable: an image is replaced by uploading another and
// deleting this one, never by editing it in place. So the cache header is as
// long as it can be, and the API sends the same.

const API_BASE = process.env.API_BASE_URL ?? "http://localhost:8000";

export async function GET(
  _req: NextRequest,
  ctx: { params: Promise<{ kind: string; id: string }> },
) {
  const { kind, id } = await ctx.params;

  // Shape-checked here so a malformed path never becomes a request to the API.
  if (!/^[a-z]+$/.test(kind) || !/^[0-9a-fA-F-]{36}$/.test(id)) {
    return new NextResponse("Not found", { status: 404 });
  }

  const upstream = await fetch(
    `${API_BASE}/api/v1/public/images/${kind}/${id}`,
    { next: { revalidate: 604800 } },
  );
  if (!upstream.ok) {
    return new NextResponse("Not found", { status: 404 });
  }

  return new NextResponse(upstream.body, {
    status: 200,
    headers: {
      "Content-Type":
        upstream.headers.get("content-type") ?? "application/octet-stream",
      "Cache-Control": "public, max-age=604800, immutable",
    },
  });
}
