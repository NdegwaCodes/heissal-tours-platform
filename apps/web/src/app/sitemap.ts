import type { MetadataRoute } from "next";
import { places, properties } from "@/lib/api";
import { canonical } from "@/lib/site";

// Built from what is actually published, not from a hand-kept list.
//
// A hand-kept sitemap is wrong the first time somebody publishes a property
// and nobody notices for a month, because nothing complains. This one asks
// the API the same question the pages ask.
//
// A withdrawn property drops out of here on its own, which matters: a sitemap
// that keeps offering a URL that now 404s is how a site loses standing with a
// crawler.
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [allPlaces, allStays] = await Promise.all([places(), properties()]);

  const fixed = ["/", "/destinations", "/stays", "/experiences", "/enquire"];

  return [
    ...fixed.map((path) => ({
      url: canonical(path),
      changeFrequency: "weekly" as const,
      priority: path === "/" ? 1 : 0.7,
    })),
    ...allPlaces.map((one) => ({
      url: canonical(`/destinations/${one.slug}`),
      changeFrequency: "weekly" as const,
      priority: 0.8,
    })),
    ...allStays.map((one) => ({
      url: canonical(`/stays/${one.slug}`),
      changeFrequency: "weekly" as const,
      priority: 0.6,
    })),
  ];
  // Activities are not listed. They have no page of their own: they are shown
  // on the destination they belong to, because a page carrying one paragraph
  // is a page a crawler learns to ignore, and there is nothing else to put on
  // it -- an activity has no photographs and no price in this system.
}
