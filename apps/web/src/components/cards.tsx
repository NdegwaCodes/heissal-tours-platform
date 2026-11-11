import Link from "next/link";
import { Photo, lead } from "@/components/photo";
import type { Experience, Place, Property } from "@/lib/types";
import { duration, titleCase } from "@/lib/utils";

// No prices on any of these, and not because they were left off: the API
// carries none (see its public allow-list), so there is no field to read. A
// "from" figure on a card would be a promise, and every figure this business
// produces depends on dates, party shape, residence and season.

export function PlaceCard({ place }: { place: Place }) {
  const photo = lead(place.images);
  return (
    <Link
      href={`/destinations/${place.slug}`}
      className="group block overflow-hidden rounded-xl border border-hairline bg-white shadow-sm transition duration-200 hover:-translate-y-1 hover:shadow-md"
    >
      <div className="aspect-[4/3] overflow-hidden bg-cream">
        {photo ? (
          <Photo
            image={photo}
            sizes="(min-width: 640px) 33vw, 100vw"
            className="transition-transform duration-500 group-hover:scale-[1.04]"
          />
        ) : null}
      </div>
      <div className="px-5 py-4">
        <p className="text-[10px] uppercase tracking-eyebrow text-gold">
          {[titleCase(place.type), place.region].filter(Boolean).join(" · ")}
        </p>
        <h3 className="mt-1.5 font-display text-2xl group-hover:text-gold">
          {place.name}
        </h3>
        {place.description ? (
          <p className="mt-2 line-clamp-3 text-[13px] leading-relaxed text-ink-soft">
            {place.description}
          </p>
        ) : null}
      </div>
    </Link>
  );
}

export function PropertyCard({ property }: { property: Property }) {
  const photo = lead(property.images);
  return (
    <Link
      href={`/stays/${property.slug}`}
      className="group block overflow-hidden rounded-xl border border-hairline bg-white shadow-sm transition duration-200 hover:-translate-y-1 hover:shadow-md"
    >
      <div className="aspect-[4/3] overflow-hidden bg-cream">
        {photo ? (
          <Photo
            image={photo}
            sizes="(min-width: 640px) 33vw, 100vw"
            className="transition-transform duration-500 group-hover:scale-[1.04]"
          />
        ) : null}
      </div>
      <div className="px-5 py-4">
        <p className="text-[10px] uppercase tracking-eyebrow text-gold">
          {[titleCase(property.category), property.destination]
            .filter(Boolean)
            .join(" · ")}
        </p>
        <h3 className="mt-1.5 font-display text-2xl group-hover:text-gold">
          {property.name}
        </h3>
        {property.description ? (
          <p className="mt-2 line-clamp-3 text-[13px] leading-relaxed text-ink-soft">
            {property.description}
          </p>
        ) : null}
      </div>
    </Link>
  );
}

export function ExperienceRow({ experience }: { experience: Experience }) {
  return (
    <li className="border-t border-hairline py-5 last:border-b">
      <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
        <h3 className="font-display text-xl">{experience.name}</h3>
        <p className="text-[12px] text-ink-soft">
          {[experience.destination, duration(experience.duration_minutes)]
            .filter(Boolean)
            .join(" · ")}
        </p>
      </div>
      {experience.description ? (
        <p className="mt-2 max-w-2xl text-[13px] leading-relaxed text-ink-soft">
          {experience.description}
        </p>
      ) : null}
    </li>
  );
}
