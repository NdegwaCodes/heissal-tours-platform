import Link from "next/link";

export default function NotFound() {
  return (
    <main className="grid min-h-dvh place-items-center px-6">
      <div className="max-w-md text-center">
        <p className="font-display text-3xl">There is nothing here</p>
        <p className="mt-3 text-sm leading-relaxed text-ink-soft">
          If you were opening your trip, use the link your consultant sent you
          rather than a typed address -- the link is what identifies your
          booking.
        </p>
        <Link
          href="/trip"
          className="mt-6 inline-block border-b border-gold pb-0.5 text-sm text-gold"
        >
          Your trip
        </Link>
      </div>
    </main>
  );
}
