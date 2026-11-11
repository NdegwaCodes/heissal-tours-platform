import { Builder } from "@/components/builder";
import { places } from "@/lib/api";
import { canonical } from "@/lib/site";

export const metadata = {
  title: "Safari builder",
  description:
    "Build a trip destination by destination and see a real, currently " +
    "published price for it — not a placeholder.",
  alternates: { canonical: canonical("/builder") },
};

// The destination list is fetched server-side (cached, like every other page)
// and handed to the client component once; the builder itself only ever
// talks to /api/estimate for a price, never to the catalogue read endpoints.
export default async function BuilderPage() {
  const destinations = await places();
  return <Builder destinations={destinations} />;
}
