/* eslint-disable @next/next/no-img-element */
import { canonical } from "@/lib/site";

export const metadata = {
  title: "Gallery",
  description:
    "Scenes from the Kenyan coast and highlands — our own photographs from the " +
    "places the trips are built around.",
  alternates: { canonical: canonical("/gallery") },
};

const EYE = "text-[11px] font-medium uppercase tracking-eyebrow text-gold";

const PHOTOS: { src: string; caption: string }[] = [
  { src: "/malindi/hero.jpg", caption: "The reef at first light" },
  { src: "/malindi/dhow.jpg", caption: "A dhow off Diani" },
  { src: "/malindi/shallows.jpg", caption: "Warm shallows, low tide" },
  { src: "/malindi/mangroves.jpg", caption: "Mangrove channels, Mida Creek" },
  { src: "/malindi/sunset.jpg", caption: "Sundowners on the water" },
  { src: "/malindi/harbour.jpg", caption: "The old harbour" },
  { src: "/malindi/kitesurf.jpg", caption: "Kitesurfing the trade winds" },
  { src: "/malindi/ocean-safari.jpg", caption: "Out past the reef edge" },
  { src: "/malindi/moorings.jpg", caption: "Moorings at dusk" },
];

export default function Gallery() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
      <p className={EYE}>Gallery</p>
      <h1 className="mt-3 max-w-2xl font-display text-4xl font-normal leading-[1.06] sm:text-5xl lg:text-6xl">
        Scenes from the coast
      </h1>
      <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-ink-soft">
        Our own photographs from the places these trips are built around — the
        reef, the dhows, the channels and the light at the end of the day.
      </p>

      <div className="mt-12 columns-1 gap-4 sm:columns-2 lg:columns-3 [&>*]:mb-4">
        {PHOTOS.map((p) => (
          <figure key={p.src} className="break-inside-avoid">
            <div className="overflow-hidden rounded-xl bg-cream">
              <img
                src={p.src}
                alt={p.caption}
                className="w-full object-cover transition duration-500 hover:scale-[1.03]"
              />
            </div>
            <figcaption className="mt-2 text-[13px] text-ink-soft">
              {p.caption}
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}
