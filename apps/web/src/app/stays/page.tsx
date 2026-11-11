import { Empty } from "@/components/empty";
import { Eyebrow } from "@/components/eyebrow";
import { PropertyCard } from "@/components/cards";
import { properties } from "@/lib/api";
import { canonical } from "@/lib/site";

export const metadata = {
  title: "Where to stay",
  description:
    "The lodges, camps and beach properties we book in Kenya, and what each one is like.",
  alternates: { canonical: canonical("/stays") },
};

export default async function Stays() {
  const all = await properties();
  return (
    <div className="mx-auto max-w-6xl px-6 py-16 sm:py-24">
      <Eyebrow>Where you stay</Eyebrow>
      <h1 className="mt-3 max-w-2xl font-display text-4xl font-normal leading-[1.1] sm:text-5xl">
        Lodges, camps and beach properties
      </h1>
      <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-ink-soft">
        These are properties we book regularly and know. A quotation normally
        offers you several, so you are choosing between real options rather than
        agreeing to one.
      </p>
      {all.length ? (
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {all.map((one) => (
            <PropertyCard key={one.slug} property={one} />
          ))}
        </div>
      ) : (
        <div className="mt-12">
          <Empty what="the properties we use" />
        </div>
      )}
    </div>
  );
}
