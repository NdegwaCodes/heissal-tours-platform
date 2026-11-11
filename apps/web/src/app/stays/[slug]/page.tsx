import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { Eyebrow } from "@/components/eyebrow";
import { EnquiryForm } from "@/components/enquiry-form";
import { JsonLd } from "@/components/json-ld";
import { Photo, lead } from "@/components/photo";
import { properties, property } from "@/lib/api";
import { canonical } from "@/lib/site";
import { titleCase } from "@/lib/utils";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return (await properties()).map((one) => ({ slug: one.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const found = await property(slug);
  if (!found) return { title: "Not found" };
  const where = found.destination ? `${found.name}, ${found.destination}` : found.name;
  return {
    title: where,
    description: found.description?.slice(0, 300) ?? undefined,
    alternates: { canonical: canonical(`/stays/${found.slug}`) },
    openGraph: {
      title: where,
      description: found.description?.slice(0, 300) ?? undefined,
      url: canonical(`/stays/${found.slug}`),
    },
  };
}

export default async function Stay({ params }: Props) {
  const { slug } = await params;
  const found = await property(slug);
  if (!found) notFound();

  const hero = lead(found.images);
  const rest = found.images.filter((one) => one.id !== hero?.id);

  return (
    <>
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "LodgingBusiness",
          name: found.name,
          description: found.description ?? undefined,
          url: canonical(`/stays/${found.slug}`),
          ...(found.star_rating
            ? { starRating: { "@type": "Rating", ratingValue: found.star_rating } }
            : {}),
          ...(found.check_in_time ? { checkinTime: found.check_in_time } : {}),
          ...(found.check_out_time ? { checkoutTime: found.check_out_time } : {}),
          ...(found.latitude && found.longitude
            ? {
                geo: {
                  "@type": "GeoCoordinates",
                  latitude: found.latitude,
                  longitude: found.longitude,
                },
              }
            : {}),
          // No priceRange, no aggregateRating and no reviews. All three are
          // things a search result displays and all three would be invented
          // here: this system holds no public price and has never collected a
          // review.
        }}
      />

      {hero ? (
        <div className="aspect-[16/7] max-h-[26rem] w-full overflow-hidden bg-cream">
          <Photo image={hero} priority sizes="100vw" />
        </div>
      ) : null}

      <div className="mx-auto max-w-5xl px-6 py-14">
        <nav className="text-[12px] text-ink-soft">
          <Link href="/stays" className="hover:text-ink">
            Where to stay
          </Link>
          {found.destination_slug ? (
            <>
              <span className="mx-2 text-gold">/</span>
              <Link
                href={`/destinations/${found.destination_slug}`}
                className="hover:text-ink"
              >
                {found.destination}
              </Link>
            </>
          ) : null}
          <span className="mx-2 text-gold">/</span>
          <span>{found.name}</span>
        </nav>

        <Eyebrow className="mt-6">
          {[titleCase(found.category), found.destination].filter(Boolean).join(" · ")}
        </Eyebrow>
        <h1 className="mt-3 font-display text-4xl sm:text-5xl">{found.name}</h1>
        {found.star_rating ? (
          <p className="oldstyle mt-2 text-[13px] text-ink-soft">
            {found.star_rating} star
          </p>
        ) : null}

        {found.description ? (
          <p className="mt-6 max-w-2xl whitespace-pre-line text-[15px] leading-relaxed text-ink-soft">
            {found.description}
          </p>
        ) : null}

        <dl className="mt-10 grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-hairline bg-hairline sm:grid-cols-3">
          {found.check_in_time ? (
            <Fact label="Check in" value={found.check_in_time} />
          ) : null}
          {found.check_out_time ? (
            <Fact label="Check out" value={found.check_out_time} />
          ) : null}
          {found.destination ? (
            <Fact label="Where" value={found.destination} />
          ) : null}
        </dl>

        {found.rooms.length ? (
          <section className="mt-14">
            <Eyebrow>Rooms</Eyebrow>
            <h2 className="mt-2 font-display text-2xl">What you can book</h2>
            <ul className="mt-5 divide-y divide-hairline border-y border-hairline">
              {found.rooms.map((room) => (
                <li key={room} className="py-3 text-[14px] text-ink-soft">
                  {room}
                </li>
              ))}
            </ul>
            {/* No rate and no availability. This system has never modelled
                availability, and a website implying it had would be lying in
                the most expensive way available. */}
            <p className="mt-3 text-[12px] text-ink-soft">
              Availability and the rate for your dates are confirmed with your
              quotation.
            </p>
          </section>
        ) : null}

        {rest.length ? (
          <div className="mt-14 grid gap-3 sm:grid-cols-3">
            {rest.slice(0, 6).map((one) => (
              <div key={one.id} className="aspect-[4/3] overflow-hidden rounded-xl bg-cream">
                <Photo image={one} sizes="(min-width: 640px) 33vw, 100vw" />
              </div>
            ))}
          </div>
        ) : null}

        <section className="mt-20 border-t border-hairline pt-12">
          <Eyebrow>Ask about it</Eyebrow>
          <h2 className="mt-2 font-display text-3xl">Stay at {found.name}</h2>
          <p className="mt-3 max-w-xl text-[14px] leading-relaxed text-ink-soft">
            Tell us your dates and party and we will confirm what is available
            and what it costs — alongside a couple of alternatives, so you are
            comparing rather than guessing.
          </p>
          <div className="mt-8 max-w-2xl">
            <EnquiryForm
              about={found.destination ? `${found.name}, ${found.destination}` : found.name}
            />
          </div>
        </section>
      </div>
    </>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-cream-tint px-4 py-4">
      <dt className="text-[10px] uppercase tracking-eyebrow text-ink-soft">
        {label}
      </dt>
      <dd className="oldstyle mt-1.5 font-display text-lg">{value}</dd>
    </div>
  );
}
