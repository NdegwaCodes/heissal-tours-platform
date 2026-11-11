/** @type {import('next').NextConfig} */

// The opposite posture to the portal's. That app is somebody's private trip
// and is noindex, no-referrer, nothing cached; this one wants to be found,
// read, shared and indexed, so the only headers here are the ones that are
// right for any public site.
//
// Still no `env` block for API_BASE_URL: Next inlines those at build time,
// which bakes one environment's backend into the artefact. src/lib/api.ts
// reads process.env at request time, and it is imported only from server
// components and route handlers.
const SECURITY_HEADERS = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
  // Send the origin, not the full path, to anywhere we link out to: a hotel or
  // an airline has no business knowing which page of ours somebody came from.
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
];

const nextConfig = {
  reactStrictMode: true,
  async headers() {
    return [{ source: "/:path*", headers: SECURITY_HEADERS }];
  },
};

export default nextConfig;
