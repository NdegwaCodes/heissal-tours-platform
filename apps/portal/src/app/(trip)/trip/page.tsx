"use client";

import Link from "next/link";
import { Eyebrow } from "@/components/eyebrow";
import { useTrip } from "@/components/trip-provider";
import { longDate, money, nights, shortDate, weekday } from "@/lib/format";
import type { Day, Stay } from "@/lib/types";

// The trip they booked.
//
// Everything on this page comes out of the version they accepted (3.4),
// through the API's allow-list. There is nothing here to widen: the payload
// has no cost, no margin and no supplier in it, and the page could not show
// one if it tried.
//
// It also shows only the option they took. A quote offers three to nine, and
// putting the two they turned down in front of somebody who has paid a
// deposit re-opens a decision.

export default function TripPage() {
  const trip = useTrip();
  const where = destinations(trip.stays) || trip.property_name || "Your trip";

  return (
    <div className="space-y-14">
      <section>
        <Eyebrow>Your itinerary</Eyebrow>
        <h1 className="mt-3 font-display text-4xl leading-tight sm:text-5xl">
          {where}
        </h1>
        {trip.status === "provisional" ? (
          <p className="mt-4 max-w-xl text-[13px] leading-relaxed text-ink-soft">
            Held for you, and confirmed once the deposit reaches us.
          </p>
        ) : null}

        <dl className="mt-8 grid grid-cols-2 gap-px overflow-hidden rounded border border-hairline bg-hairline sm:grid-cols-4">
          <Stat label="Arriving" value={longDate(trip.arrival_date) || "-"} />
          <Stat label="Leaving" value={longDate(trip.departure_date) || "-"} />
          <Stat label="Nights" value={trip.nights ? nights(trip.nights) : "-"} />
          <Stat
            label="Guests"
            value={trip.pax_count ? String(trip.pax_count) : "-"}
          />
        </dl>
      </section>

      <section className="print-open bg-panel px-7 py-8 text-panel-ink">
        <Eyebrow className="text-gold-soft">What you agreed</Eyebrow>
        <p className="oldstyle mt-3 font-display text-4xl">
          {money(trip.total, trip.currency)}
        </p>
        <p className="mt-3 max-w-xl text-[13px] leading-relaxed text-gold-soft">
          The total for the whole party, fixed at the point of booking. It does
          not move if our prices change afterwards.{" "}
          <Link href="/statement" className="no-print underline">
            What is paid, and what is due
          </Link>
        </p>
      </section>

      {trip.stays.length > 1 ? (
        <section>
          <Eyebrow>Where you are staying</Eyebrow>
          <ul className="mt-5 divide-y divide-hairline border-y border-hairline">
            {trip.stays.map((stay) => (
              <StayRow key={stay.sequence} stay={stay} />
            ))}
          </ul>
        </section>
      ) : (
        <section>
          <Eyebrow>Where you are staying</Eyebrow>
          <h2 className="mt-3 font-display text-3xl">{trip.property_name}</h2>
          <p className="mt-2 text-[13px] text-ink-soft">
            {[trip.room_type, trip.board].filter(Boolean).join(" - ")}
          </p>
          {trip.description ? (
            <p className="mt-5 max-w-2xl text-[15px] leading-relaxed text-ink-soft">
              {trip.description}
            </p>
          ) : null}
        </section>
      )}

      {trip.days.length ? (
        <section>
          <Eyebrow>Day by day</Eyebrow>
          <ol className="mt-6 space-y-px">
            {trip.days.map((day) => (
              <DayRow key={day.number} day={day} />
            ))}
          </ol>
        </section>
      ) : (
        <section>
          <Eyebrow>Day by day</Eyebrow>
          {/* A quote can be priced and accepted before its programme is
              written (4.1 is a separate step), and an empty list would read
              as a trip with nothing in it. */}
          <p className="mt-4 max-w-xl text-[15px] leading-relaxed text-ink-soft">
            Your day-by-day programme is still being put together. Your
            consultant will let you know as soon as it is ready.
          </p>
        </section>
      )}

      {trip.included.length ? (
        <section className="print-open">
          <Eyebrow>Included</Eyebrow>
          <ul className="mt-5 grid gap-x-10 gap-y-2 sm:grid-cols-2">
            {trip.included.map((item) => (
              <li
                key={item}
                className="flex gap-3 text-[14px] leading-relaxed text-ink-soft"
              >
                <span aria-hidden className="text-gold">
                  &bull;
                </span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
          {/* No "not included" list. The API does not carry one, and one
              written here would be this app's guess at a commercial term. */}
        </section>
      ) : null}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-cream-tint px-4 py-4">
      <dt className="text-[10px] uppercase tracking-eyebrow text-ink-soft">
        {label}
      </dt>
      <dd className="oldstyle mt-1.5 font-display text-lg leading-snug">
        {value}
      </dd>
    </div>
  );
}

function StayRow({ stay }: { stay: Stay }) {
  return (
    <li className="print-open flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 py-4">
      <div>
        <p className="font-display text-xl">{stay.property_name}</p>
        <p className="mt-1 text-[12px] text-ink-soft">
          {[stay.destination, stay.room_type, stay.board]
            .filter(Boolean)
            .join(" - ")}
        </p>
      </div>
      <p className="oldstyle text-[13px] text-ink-soft">
        {stay.nights ? nights(stay.nights) : ""}
        {stay.rooms ? ` - ${stay.rooms} ${stay.rooms === 1 ? "room" : "rooms"}` : ""}
      </p>
    </li>
  );
}

function DayRow({ day }: { day: Day }) {
  const marks = [
    day.is_arrival ? "Arrival" : null,
    day.is_departure ? "Departure" : null,
  ].filter(Boolean);

  return (
    <li className="print-open border-t border-hairline py-6 last:border-b sm:grid sm:grid-cols-[7rem_1fr] sm:gap-8">
      <div className="shrink-0">
        <p className="oldstyle font-display text-2xl leading-none">
          Day {day.number}
        </p>
        {day.date ? (
          <p className="oldstyle mt-1.5 text-[12px] text-ink-soft">
            {weekday(day.date)}
            <br />
            {shortDate(day.date)}
          </p>
        ) : null}
      </div>

      <div className="mt-3 sm:mt-0">
        <p className="font-display text-xl">
          {day.destination || day.property_name || "\u2014"}
        </p>

        {day.movements.length ? (
          <ul className="mt-3 space-y-1">
            {day.movements.map((move, i) => (
              <li key={`${move.label}-${i}`} className="text-[13px] text-ink-soft">
                <span className="text-gold">&rarr;</span> {move.label}
                {/* Drive times only where the route table has one (4.2).
                    Inventing an estimate for a road nobody has measured is
                    how a client misses a gate closing. */}
                {move.minutes ? (
                  <span className="oldstyle"> ({hours(move.minutes)})</span>
                ) : null}
              </li>
            ))}
          </ul>
        ) : null}

        {day.excursions.length ? (
          <ul className="mt-3 space-y-1">
            {day.excursions.map((one) => (
              <li key={one} className="text-[13px] text-ink-soft">
                <span className="text-gold">&bull;</span> {one}
              </li>
            ))}
          </ul>
        ) : null}

        <p className="mt-3 text-[12px] text-ink-soft">
          {day.has_night
            ? [day.property_name, day.board].filter(Boolean).join(" - ")
            : "No overnight stay"}
          {marks.length ? (
            <span className="ml-2 text-gold">{marks.join(" & ")}</span>
          ) : null}
        </p>
      </div>
    </li>
  );
}

function destinations(stays: Stay[]): string {
  const seen: string[] = [];
  for (const stay of stays) {
    if (stay.destination && !seen.includes(stay.destination)) {
      seen.push(stay.destination);
    }
  }
  if (seen.length <= 1) return seen[0] ?? "";
  return `${seen.slice(0, -1).join(", ")} & ${seen[seen.length - 1]}`;
}

function hours(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m ? `${h} hr ${m} min` : `${h} hr`;
}
