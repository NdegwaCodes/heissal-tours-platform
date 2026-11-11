"use client";
/* eslint-disable @next/next/no-img-element */

import Link from "next/link";
import { useState } from "react";

type Region = "coast" | "highlands" | "both";
type Card = {
  id: string;
  region: Region;
  kicker: string;
  title: string;
  desc: string;
  nights: number;
  price: string;
  img: string;
  href: string;
};

const CARDS: Card[] = [
  { id: "ocean", region: "both", kicker: "Coast & Highlands", title: "Ocean and Altitude",
    desc: "The full arc: sea level to the northern slopes, one country, two climates.",
    nights: 12, price: "from $9,400 pp", img: "/malindi/dhow.jpg", href: "/itineraries/ocean-and-altitude" },
  { id: "fournights", region: "coast", kicker: "Coast · Diani", title: "Four Nights on the South Coast",
    desc: "A short add-on for anyone already in Kenya, or anyone with a long layover.",
    nights: 4, price: "Enquire for pricing", img: "/malindi/shallows.jpg", href: "/enquire" },
  { id: "children", region: "highlands", kicker: "Highlands · Nanyuki", title: "Highlands with Children",
    desc: "Short drives, a farm to run around, and game viewing that does not need silence.",
    nights: 7, price: "from $5,400 pp", img: "/malindi/mangroves.jpg", href: "/enquire" },
  { id: "plains", region: "both", kicker: "Safari · Maasai Mara", title: "Plains and the Migration",
    desc: "The open Mara in the months the herds move, with a few nights on the coast to slow down after.",
    nights: 9, price: "from $7,200 pp", img: "/malindi/sunset.jpg", href: "/enquire" },
  { id: "chale", region: "coast", kicker: "Coast · Diani", title: "The Chale Reef",
    desc: "Five minutes from the reef edge, with a dhow on standby and nothing on the calendar.",
    nights: 7, price: "from $4,850 pp", img: "/malindi/harbour.jpg", href: "/enquire" },
  { id: "mtkenya", region: "highlands", kicker: "Highlands · Nanyuki", title: "Mount Kenya & Laikipia",
    desc: "Conservancy game drives at 1,950m, with the mountain visible from breakfast.",
    nights: 8, price: "from $6,200 pp", img: "/malindi/moorings.jpg", href: "/enquire" },
];

const REGIONS: [string, string][] = [["all", "All"], ["coast", "Coast"], ["highlands", "Highlands"], ["both", "Both"]];
const LENGTHS: [string, string][] = [["any", "Any"], ["up6", "Up to 6"], ["7-9", "7–9"], ["10plus", "10+"]];
const EYE = "text-[11px] font-medium uppercase tracking-eyebrow text-gold";

export default function DestinationsView() {
  const [region, setRegion] = useState("all");
  const [length, setLength] = useState("any");

  const inLength = (n: number) =>
    length === "any" || (length === "up6" ? n <= 6 : length === "7-9" ? n >= 7 && n <= 9 : n >= 10);
  const shown = CARDS.filter((c) => (region === "all" || c.region === region) && inLength(c.nights));

  return (
    <>
      <section className="border-b border-hairline bg-cream-tint">
        <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 px-6 py-8">
          <div>
            <p className={EYE}>Diani · Watamu</p>
            <p className="mt-1 font-display text-2xl">The coast</p>
          </div>
          <div>
            <p className={EYE}>Nanyuki · Mount Kenya</p>
            <p className="mt-1 font-display text-2xl">The highlands</p>
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
        <p className={EYE}>Itineraries</p>
        <h1 className="mt-3 max-w-2xl font-display text-4xl font-normal leading-[1.06] sm:text-5xl lg:text-6xl">
          Trips we run, ready to be changed
        </h1>
        <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-ink-soft">
          Every itinerary here is a real route with real properties. Prices are
          indicative, for two sharing, and only shown where the rate data is complete.
        </p>

        <div className="mt-10 flex flex-wrap gap-x-14 gap-y-6">
          <Filter label="Region" opts={REGIONS} val={region} set={setRegion} />
          <Filter label="Length" opts={LENGTHS} val={length} set={setLength} />
        </div>

        <div className="mt-8 border-t border-hairline" />

        {shown.length ? (
          <div className="mt-12 grid gap-x-8 gap-y-14 sm:grid-cols-2 lg:grid-cols-3">
            {shown.map((c) => (
              <Link key={c.id} href={c.href} className="group block">
                <div className="aspect-[4/3] overflow-hidden rounded-xl bg-cream">
                  <img src={c.img} alt="" className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.03]" />
                </div>
                <p className="mt-5 text-[11px] uppercase tracking-eyebrow text-gold">{c.kicker}</p>
                <h3 className="mt-2 font-display text-2xl group-hover:text-gold">{c.title}</h3>
                <p className="mt-2 text-[14px] leading-relaxed text-ink-soft">{c.desc}</p>
                <div className="mt-5 flex items-center gap-3 border-t border-hairline pt-4 text-[13px]">
                  <span>{c.nights} nights</span>
                  <span className="text-hairline">/</span>
                  <span className="text-ink-soft">{c.price}</span>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <p className="mt-12 text-[15px] text-ink-soft">
            No itineraries match that combination yet &mdash; widen the filters, or{" "}
            <Link href="/enquire" className="border-b border-gold text-gold">tell us what you have in mind</Link>.
          </p>
        )}
      </div>
    </>
  );
}

function Filter({ label, opts, val, set }: { label: string; opts: [string, string][]; val: string; set: (v: string) => void }) {
  return (
    <div>
      <p className="text-[11px] uppercase tracking-eyebrow text-gold">{label}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {opts.map(([id, lbl]) => (
          <button
            key={id}
            type="button"
            onClick={() => set(id)}
            className={"rounded-full border px-4 py-2 text-[13px] transition duration-200 " + (val === id ? "border-ink bg-ink text-paper shadow-sm" : "border-hairline text-ink hover:border-gold hover:bg-cream-tint")}
          >
            {lbl}
          </button>
        ))}
      </div>
    </div>
  );
}
