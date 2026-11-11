/** @type {import('next').NextConfig} */

// Headers, and why each one is here rather than left to a default.
//
// no-referrer: the whole point of putting the grant token in the link's
// fragment (7.2) is that it never reaches a server. An itinerary page that
// links out to an airline or a hotel would otherwise leak the *portal* URL in
// a Referer header, and the day somebody puts a token back into a query
// string that becomes a live credential in a third party's access log. The
// header makes that mistake harmless in advance.
//
// noindex: a client forwards their link into a family group chat, and one of
// those is a public forum often enough. robots.txt asks a crawler not to
// index; X-Robots-Tag tells it not to, and covers the JSON and the rendered
// proposal too.
const SECURITY_HEADERS = [
  { key: "Referrer-Policy", value: "no-referrer" },
  { key: "X-Robots-Tag", value: "noindex, nofollow, noarchive" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  // SAMEORIGIN rather than DENY: /document renders the accepted proposal in
  // an iframe of our own.
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
];

const nextConfig = {
  reactStrictMode: true,
  // No `env` block for API_BASE_URL, deliberately. Next inlines those at
  // BUILD time, which bakes one environment's backend address into the
  // artefact -- staging and production would need two builds, and a wrong one
  // is not visible until a page is opened. src/lib/session.ts reads
  // process.env at request time instead; it is imported only by the two route
  // handlers, so the value never reaches the browser either way.
  async headers() {
    return [{ source: "/:path*", headers: SECURITY_HEADERS }];
  },
};

export default nextConfig;
