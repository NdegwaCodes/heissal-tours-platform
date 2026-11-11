"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Eyebrow } from "@/components/eyebrow";
import type { Estimate, Place } from "@/lib/types";
import { money } from "@/lib/format";

// The safari builder, priced for real.
//
// Every property name, room type and figure a visitor sees here comes back
// from POST /api/estimate -> the API's own build-up arithmetic against real,
// published, currently-active rates (app/modules/public/estimate.py). This
// component holds no property list, no rate table and no profit formula of
// its own -- there is nothing here for it to get out of step with the real
// engine, because it does not have a competing copy to drift.
//
// It cannot show a price for a destination and comfort level nothing is
// filed for. Where the API refuses a leg, this shows the API's own reason
// rather than inventing a placeholder figure, because a number with nothing
// behind it is worse than an honest "ask us".

const TIERS: { id: string; label: string; note: string }[] = [
  { id: "comfort", label: "Comfort", note: "Well-run camps and small hotels (1-3 star)" },
  { id: "luxury", label: "Luxury", note: "The kind we would book for ourselves (4 star)" },
  { id: "ultra", label: "Ultra", note: "The best address in each place (5 star)" },
];

type Leg = { destination: string; nights: number };

const EYE = "text-[11px] font-medium uppercase tracking-eyebrow text-gold";

export function Builder({ destinations }: { destinations: Place[] }) {
  const [trip, setTrip] = useState<Leg[]>(
    destinations.slice(0, 1).map((d) => ({ destination: d.slug, nights: 5 })),
  );
  const [tier, setTier] = useState("luxury");
  const [resident, setResident] = useState(false);
  const [adults, setAdults] = useState(2);
  const [children, setChildren] = useState(0);

  const [estimate, setEstimate] = useState<Estimate | null>(null);
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState(false);

  const byRoom: Record<string, string> = useMemo(
    () => Object.fromEntries(destinations.map((d) => [d.slug, d.name])),
    [destinations],
  );

  // Debounced: every nights/tier/party change would otherwise fire a request
  // per keystroke on the stepper buttons.
  useEffect(() => {
    if (trip.length === 0) {
      setEstimate(null);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      setFailed(false);
      try {
        const res = await fetch("/api/estimate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            resident,
            adults,
            children,
            legs: trip.map((l) => ({ destination: l.destination, tier, nights: l.nights })),
          }),
        });
        if (!res.ok) {
          setFailed(true);
          setEstimate(null);
          return;
        }
        setEstimate((await res.json()) as Estimate);
      } catch {
        setFailed(true);
        setEstimate(null);
      } finally {
        setLoading(false);
      }
    }, 350);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trip, tier, resident, adults, children]);

  const setNights = (i: number, n: number) =>
    setTrip(trip.map((l, j) => (j === i ? { ...l, nights: Math.max(1, n) } : l)));
  const removeLeg = (i: number) => setTrip(trip.filter((_, j) => j !== i));
  const addPlace = (slug: string) =>
    setTrip((prev) => [...prev, { destination: slug, nights: 3 }]);

  const available = destinations.filter(
    (d) => !trip.some((l) => l.destination === d.slug),
  );
  const partyLabel =
    adults + " " + (adults === 1 ? "adult" : "adults") +
    (children ? ", " + children + " " + (children === 1 ? "child" : "children") : "");

  return (
    <div className="mx-auto max-w-6xl px-6 py-16 sm:py-24">
      <p className={EYE}>Safari builder</p>
      <h1 className="mt-3 max-w-2xl font-display text-4xl font-normal leading-[1.06] sm:text-5xl lg:text-6xl">
        Build the trip and watch the price
      </h1>
      <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-ink-soft">
        Every figure below comes from a real, currently published rate — never
        a placeholder. Where we do not yet have one for a destination and
        comfort level, we say so rather than guess.
      </p>

      {destinations.length === 0 ? (
        <div className="mt-10 rounded-xl border border-hairline bg-cream-tint px-6 py-8 shadow-sm">
          <p className="text-[14px] leading-relaxed text-ink-soft">
            We are still publishing destinations. Tell us what you have in mind
            instead, and a consultant will put real figures to it.
          </p>
          <Link
            href="/enquire"
            className="mt-4 inline-block border-b border-gold pb-0.5 text-[13px] text-gold"
          >
            Start an enquiry
          </Link>
        </div>
      ) : (
        <div className="mt-12 grid gap-10 lg:grid-cols-[1fr_380px]">
          <div className="flex flex-col gap-10">
            <div>
              <p className={EYE}>Comfort level</p>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                {TIERS.map((t) => {
                  const on = t.id === tier;
                  return (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setTier(t.id)}
                      className={
                        "rounded-xl border p-5 text-left transition duration-200 " +
                        (on
                          ? "border-gold bg-cream-tint shadow-sm ring-1 ring-gold/30"
                          : "border-hairline hover:border-gold hover:shadow-sm")
                      }
                    >
                      <span className="font-display text-xl">{t.label}</span>
                      <span className="mt-1 block text-[12px] leading-snug text-ink-soft">
                        {t.note}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <h2 className="border-b border-hairline pb-4 font-display text-2xl">
                Your trip
              </h2>
              {trip.length === 0 ? (
                <p className="mt-6 text-[14px] text-ink-soft">
                  No places yet — add one below.
                </p>
              ) : null}
              {trip.map((l, i) => {
                const leg = estimate?.legs[i];
                return (
                  <div key={`${l.destination}-${i}`} className="border-b border-hairline py-6">
                    <div className="flex items-start justify-between">
                      <p className="font-display text-2xl">{byRoom[l.destination] ?? l.destination}</p>
                      <button
                        type="button"
                        onClick={() => removeLeg(i)}
                        className="text-[11px] uppercase tracking-eyebrow text-gold hover:text-ink"
                      >
                        Remove
                      </button>
                    </div>
                    <div className="mt-5">
                      <p className={EYE}>Nights</p>
                      <div className="mt-3 flex items-center gap-3">
                        <Stepper value={l.nights} onChange={(n) => setNights(i, n)} min={1} />
                      </div>
                    </div>
                    <div className="mt-5">
                      {leg?.refused ? (
                        <p className="text-[13px] leading-relaxed text-ink-soft">
                          {leg.refused}
                        </p>
                      ) : leg?.property_name ? (
                        <>
                          <p className="text-[15px]">
                            {leg.property_name}
                            {leg.room_type ? ` — ${leg.room_type}` : ""}
                            {leg.meal_plan ? ` (${leg.meal_plan})` : ""}
                          </p>
                          <div className="mt-3 flex items-baseline gap-4">
                            <span className={EYE}>Subtotal</span>
                            <span className="font-display text-2xl tabular-nums">
                              {leg.per_person && leg.currency
                                ? money(leg.per_person, leg.currency)
                                : "—"}
                            </span>
                          </div>
                        </>
                      ) : (
                        <p className="text-[13px] text-ink-soft">
                          {loading ? "Pricing this leg…" : "—"}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
              {available.length ? (
                <div className="pt-6">
                  <p className={EYE}>Add a destination</p>
                  <div className="mt-4 flex flex-wrap gap-3">
                    {available.map((d) => (
                      <button
                        key={d.slug}
                        type="button"
                        onClick={() => addPlace(d.slug)}
                        className="rounded-full border border-hairline px-4 py-2 text-[14px] text-ink transition duration-200 hover:border-gold hover:bg-cream-tint"
                      >
                        + {d.name}
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>

            <div>
              <p className={EYE}>Who is travelling</p>
              <div className="mt-5 grid gap-8 sm:grid-cols-2">
                <div>
                  <p className="text-[11px] uppercase tracking-eyebrow text-ink-soft">
                    Residency
                  </p>
                  <div className="mt-3 inline-flex rounded-full border border-hairline p-1">
                    <button
                      type="button"
                      onClick={() => setResident(true)}
                      className={"rounded-full px-5 py-2.5 text-[13px] transition duration-200 " + (resident ? "bg-panel text-panel-ink shadow-sm" : "text-ink hover:text-gold")}
                    >
                      Resident
                    </button>
                    <button
                      type="button"
                      onClick={() => setResident(false)}
                      className={"rounded-full px-5 py-2.5 text-[13px] transition duration-200 " + (!resident ? "bg-panel text-panel-ink shadow-sm" : "text-ink hover:text-gold")}
                    >
                      Non-resident
                    </button>
                  </div>
                </div>
                <div>
                  <p className="text-[11px] uppercase tracking-eyebrow text-ink-soft">
                    Children
                  </p>
                  <p className="mt-3 max-w-sm text-[13px] leading-relaxed text-ink-soft">
                    Priced as adults here — most properties charge under-12s
                    less, and your consultant applies the exact rate once you
                    have chosen one.
                  </p>
                  <div className="mt-4 flex items-center gap-3">
                    <Stepper value={children} onChange={setChildren} min={0} max={10} />
                  </div>
                </div>
              </div>
              <div className="mt-8">
                <p className="text-[11px] uppercase tracking-eyebrow text-ink-soft">Adults</p>
                <div className="mt-3 flex items-center gap-3">
                  <Stepper value={adults} onChange={setAdults} min={1} max={20} />
                </div>
              </div>
            </div>
          </div>

          <aside
            className="h-fit rounded-xl border border-hairline shadow-md lg:sticky lg:top-24"
            style={{ background: "#fffdf9" }}
          >
            <div className="p-6">
              <p className={EYE}>Your price, as built</p>
              {failed ? (
                <p className="mt-3 text-[13px] leading-relaxed text-ink-soft">
                  That could not be priced just now. Please try again in a
                  moment, or send us an enquiry directly.
                </p>
              ) : estimate?.currency && estimate.group_total ? (
                <>
                  <p className="mt-3 font-display text-5xl tabular-nums">
                    {money(estimate.per_person ?? "0", estimate.currency)}
                  </p>
                  <p className="mt-1 text-[13px] text-ink-soft">per person</p>
                  <div className="mt-5 flex items-baseline justify-between border-t border-hairline pt-5">
                    <span className="text-[15px]">Total for {partyLabel}</span>
                    <span className="font-display text-2xl tabular-nums">
                      {money(estimate.group_total, estimate.currency)}
                    </span>
                  </div>
                </>
              ) : (
                <p className="mt-3 text-[13px] leading-relaxed text-ink-soft">
                  {loading
                    ? "Pricing your trip…"
                    : estimate?.legs.some((l) => l.refused)
                      ? "One or more legs above have no current rate to show — ask us and we will confirm one directly."
                      : estimate && estimate.legs.length > 1
                        ? "These legs price in different currencies, so we show each on its own rather than add them together."
                        : "Add a destination to see a price."}
                </p>
              )}
              <p className="mt-4 text-[12px] leading-relaxed text-ink-soft">
                {estimate?.note ??
                  "Indicative only. A consultant confirms every figure — including child pricing, transfers and park fees — before you pay anything."}
              </p>
              <Link
                href="/enquire"
                className="mt-6 block rounded-lg bg-panel px-5 py-4 text-center text-[12px] font-medium uppercase tracking-eyebrow text-panel-ink transition duration-200 hover:bg-ink hover:shadow-md"
              >
                Send this to us
              </Link>
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}

function Stepper({
  value,
  onChange,
  min,
  max,
}: {
  value: number;
  onChange: (n: number) => void;
  min: number;
  max?: number;
}) {
  return (
    <>
      <button
        type="button"
        onClick={() => onChange(Math.max(min, value - 1))}
        className="grid h-10 w-10 place-items-center rounded-lg border border-hairline text-xl transition duration-200 hover:border-gold hover:bg-cream-tint"
      >
        &minus;
      </button>
      <span className="w-8 text-center font-display text-3xl tabular-nums">{value}</span>
      <button
        type="button"
        onClick={() => onChange(max ? Math.min(max, value + 1) : value + 1)}
        className="grid h-10 w-10 place-items-center rounded-lg border border-hairline text-xl transition duration-200 hover:border-gold hover:bg-cream-tint"
      >
        +
      </button>
    </>
  );
}
