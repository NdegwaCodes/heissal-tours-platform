/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import { canonical } from "@/lib/site";

export const metadata = {
  title: "About",
  description:
    "Heissal Tours is run by the people who host the trips — a small team on the " +
    "Kenyan coast and in the highlands who only sell what they have slept in.",
  alternates: { canonical: canonical("/about") },
};

const EYE = "text-[11px] font-medium uppercase tracking-eyebrow text-gold";

const POINTS: { k: string; t: string; d: string }[] = [
  {
    k: "How we work",
    t: "We only sell what we have slept in",
    d: "Every property on this site is one we have stayed in ourselves. If we would not book it for our own family, it does not go on the list — which is why some routes are short and why some months are quiet.",
  },
  {
    k: "Where we are",
    t: "We run the coast ourselves",
    d: "We are based between Diani and Watamu, with people we have worked with for years in Nanyuki and the Mara. When you are on a trip, the person answering the phone is the person who arranged it.",
  },
  {
    k: "How we price",
    t: "We price in the open",
    d: "The builder shows a real, itemised price as you go — nights, flights, fees, experiences — with nothing hidden behind an enquiry. We confirm every line against live availability before you pay anything.",
  },
];

export default function About() {
  return (
    <>
      <section className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
        <p className={EYE}>About</p>
        <h1 className="mt-3 max-w-2xl font-display text-4xl font-normal leading-[1.06] sm:text-5xl lg:text-6xl">
          The people behind the trips
        </h1>
        <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-ink-soft">
          Heissal Tours is a small team who live where we send you. We build
          tailor-made safaris and coast escapes the way we would plan our own —
          slowly, honestly, and with the phone answered.
        </p>
      </section>

      <div className="mx-auto max-w-6xl px-6">
        <div className="aspect-[16/7] overflow-hidden rounded-2xl bg-cream">
          <img
            src="/malindi/dhow.jpg"
            alt="A dhow off the Kenyan coast"
            className="h-full w-full object-cover"
          />
        </div>
      </div>

      <section className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
        <div className="grid gap-x-8 gap-y-12 sm:grid-cols-3">
          {POINTS.map((p) => (
            <div key={p.t}>
              <p className={EYE}>{p.k}</p>
              <h2 className="mt-3 font-display text-2xl">{p.t}</h2>
              <p className="mt-3 text-[14px] leading-relaxed text-ink-soft">
                {p.d}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-t border-hairline bg-panel text-panel-ink">
        <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-16 sm:flex-row sm:items-center sm:justify-between sm:py-20">
          <div>
            <p className="text-[11px] font-medium uppercase tracking-eyebrow text-gold-soft">
              Start a trip
            </p>
            <h2 className="mt-3 max-w-xl font-display text-3xl leading-tight sm:text-4xl">
              Tell us roughly what you have in mind
            </h2>
            <p className="mt-4 max-w-md text-[15px] leading-relaxed text-gold-soft">
              Build it yourself and watch the price, or send us a line and we
              will come back with a route.
            </p>
          </div>
          <div className="flex flex-shrink-0 flex-wrap gap-3">
            <Link
              href="/builder"
              className="rounded-lg bg-[#f7f3ec] px-7 py-4 text-[12px] font-medium uppercase tracking-[0.13em] text-ink transition duration-200 hover:-translate-y-0.5 hover:bg-gold-soft hover:shadow-md"
            >
              Build a trip
            </Link>
            <Link
              href="/enquire"
              className="rounded-lg border border-gold-soft px-7 py-4 text-[12px] font-medium uppercase tracking-[0.13em] text-panel-ink transition duration-200 hover:bg-white/5"
            >
              Enquire
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
