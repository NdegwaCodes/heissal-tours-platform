import type { MetadataRoute } from "next";

// Belt to the X-Robots-Tag header's braces (see next.config.mjs). A client's
// itinerary and statement are not public documents, and a link forwarded into
// a public forum should not become a search result.
export default function robots(): MetadataRoute.Robots {
  return { rules: [{ userAgent: "*", disallow: "/" }] };
}
