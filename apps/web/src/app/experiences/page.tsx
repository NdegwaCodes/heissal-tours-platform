import { Empty } from "@/components/empty";
import { Eyebrow } from "@/components/eyebrow";
import { ExperienceRow } from "@/components/cards";
import { experiences } from "@/lib/api";
import { canonical } from "@/lib/site";

export const metadata = {
  title: "Things to do",
  description:
    "Game drives, dhow trips, walks and day excursions we build into Kenyan itineraries.",
  alternates: { canonical: canonical("/experiences") },
};

export default async function Experiences() {
  const all = await experiences();
  const byPlace = new Map<string, typeof all>();
  for (const one of all) {
    const key = one.destination || "Elsewhere";
    byPlace.set(key, [...(byPlace.get(key) ?? []), one]);
  }
  return (
    <div className="mx-auto max-w-6xl px-6 py-16 sm:py-24">
      <Eyebrow>Things to do</Eyebrow>
      <h1 className="mt-3 max-w-2xl font-display text-4xl font-normal leading-[1.1] sm:text-5xl">
        What goes into a day
      </h1>
      <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-ink-soft">
        These are the excursions and drives we build itineraries out of. Some
        are included in a package as standard and some are added &mdash; your
        quotation says which, per option.
      </p>
      {all.length ? (
        <div className="mt-12 space-y-14">
          {[...byPlace.entries()].map(([where, rows]) => (
            <section key={where}>
              <h2 className="font-display text-2xl">{where}</h2>
              <ul className="mt-4">
                {rows.map((one) => (
                  <ExperienceRow key={one.slug} experience={one} />
                ))}
              </ul>
            </section>
          ))}
        </div>
      ) : (
        <div className="mt-12">
          <Empty what="the excursions we offer" />
        </div>
      )}
    </div>
  );
}
