import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { Eyebrow } from "@/components/eyebrow";
import { EnquiryForm } from "@/components/enquiry-form";
import { JsonLd } from "@/components/json-ld";
import { Photo, lead } from "@/components/photo";
import { PropertyCard } from "@/components/cards";
import { ExperienceRow } from "@/components/cards";
import { experiences, place, places, properties } from "@/lib/api";
import { canonical } from "@/lib/site";
import { titleCase } from "@/lib/utils";

type Props = { params: Promise<{ slug: string }> };

// Pre-rendered at build for what is published now, and any destination
// published afterwards renders on first request and is then cached. Which is
// why this is not `dynamicParams: false`: publishing a destination must not
// need a deploy to become a page.
export async function generateStaticParams() {
  return (await places()).map((one) => ({ slug: one.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const found = await place(slug);
  if (!found) return { title: "Not found" };
  return {
    title: found.name,
    // The destination's own paragraph, trimmed. Not a keyword-stuffed
    // sentence assembled here: this is the copy somebody wrote about the
    // place, and it is the same copy the proposal uses.
    description: found.description?.slice(0, 300) ?? undefined,
    alternates: { canonical: canonical(`/destinations/${found.slug}`) },
    openGraph: {
      title: found.name,
      description: found.description?.slice(0, 300) ?? undefined,
      url: canonical(`/destinations/${found.slug}`),
    },
  };
}

export default async function Destination({ params }: Props) {
  const { slug } = await params;
  const found = await place(slug);
  // The API answers 404 for a destination that is unpublished, withdrawn or
  // deactivated, and this app does not distinguish those: a visitor gets a
  // page that offers them somewhere else to go, which is the only useful
  // thing to do about it.
  if (!found) notFound();

  const [stays, doing] = await Promise.all([
    properties(found.slug),
    experiences(found.slug),
  ]);
  const hero = lead(found.images);
  const rest = found.images.filter((one) => one.id !== hero?.id);

  return (
    <>
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "TouristDestination",
          name: found.name,
          description: found.description ?? undefined,
          url: canonical(`/destinations/${found.slug}`),
          address: {
            "@type": "PostalAddress",
            addressCountry: found.country || "KE",
            addressRegion: found.region ?? undefined,
          },
          // Only where the catalogue actually holds coordinates. An invented
          // latitude puts a pin in the sea.
          ...(found.latitude && found.longitude
            ? {
                geo: {
                  "@type": "GeoCoordinates",
                  latitude: found.latitude,
                  longitude: found.longitude,
                },
              }
            : {}),
        }}
      />

      {hero ? (
        <div className="aspect-[16/7] max-h-[26rem] w-full overflow-hidden bg-cream">
          <Photo image={hero} priority sizes="100vw" />
        </div>
      ) : null}

      <div className="mx-auto max-w-5xl px-6 py-14">
        <nav className="text-[12px] text-ink-soft">
          <Link href="/destinations" className="hover:text-ink">
            Destinations
          </Link>
          <span className="mx-2 text-gold">/</span>
          <span>{found.name}</span>
        </nav>

        <Eyebrow className="mt-6">
          {[titleCase(found.type), found.region, found.country]
            .filter(Boolean)
            .join(" · ")}
        </Eyebrow>
        <h1 className="mt-3 font-display text-4xl sm:text-5xl">{found.name}</h1>
        {found.description ? (
          <p className="mt-6 max-w-2xl whitespace-pre-line text-[15px] leading-relaxed text-ink-soft">
            {found.description}
          </p>
        ) : null}

        {rest.length ? (
          <div className="mt-10 grid gap-3 sm:grid-cols-3">
            {rest.slice(0, 6).map((one) => (
              <div key={one.id} className="aspect-[4/3] overflow-hidden rounded-xl bg-cream">
                <Photo image={one} sizes="(min-width: 640px) 33vw, 100vw" />
              </div>
            ))}
          </div>
        ) : null}

        {doing.length ? (
          <section className="mt-16">
            <Eyebrow>Things to do</Eyebrow>
            <h2 className="mt-2 font-display text-3xl">
              What people do in {found.name}
            </h2>
            <ul className="mt-6">
              {doing.map((one) => (
                <ExperienceRow key={one.slug} experience={one} />
              ))}
            </ul>
          </section>
        ) : null}

        {stays.length ? (
          <section className="mt-16">
            <Eyebrow>Where you stay</Eyebrow>
            <h2 className="mt-2 font-display text-3xl">
              Properties in {found.name}
            </h2>
            <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {stays.map((one) => (
                <PropertyCard key={one.slug} property={one} />
              ))}
            </div>
          </section>
        ) : null}

        <section className="mt-20 border-t border-hairline pt-12">
          <Eyebrow>Plan it</Eyebrow>
          <h2 className="mt-2 font-display text-3xl">
            A trip to {found.name}
          </h2>
          <p className="mt-3 max-w-xl text-[14px] leading-relaxed text-ink-soft">
            Tell us when and how many, and a consultant will come back with
            properties, a day-by-day and a price for your party.
          </p>
          <div className="mt-8 max-w-2xl">
            <EnquiryForm about={found.name} />
          </div>
        </section>
      </div>
    </>
  );
}
