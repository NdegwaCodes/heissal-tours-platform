"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { WORDMARK, WORDMARK_SUB } from "@/lib/brand";
import { longDate } from "@/lib/format";
import { useTrip } from "@/components/trip-provider";
import { cn } from "@/lib/utils";

const PAGES = [
  { href: "/trip", label: "Your trip" },
  { href: "/statement", label: "Payments" },
  { href: "/document", label: "Proposal" },
];

// Three pages, and no fourth. There is no profile, no settings, no messages
// and no sign-out, because there is no account -- see 7.2 on why a client is
// not a `users` row.

export function Chrome({ children }: { children: React.ReactNode }) {
  const trip = useTrip();
  const here = usePathname();

  return (
    <div className="min-h-dvh">
      <header className="bg-panel text-panel-ink">
        <div className="mx-auto flex max-w-4xl flex-wrap items-baseline justify-between gap-3 px-6 py-6">
          <div>
            <p className="font-display text-xl tracking-[0.22em]">{WORDMARK}</p>
            <p className="mt-1 text-[10px] uppercase tracking-eyebrow text-gold-soft">
              {WORDMARK_SUB}
            </p>
          </div>
          <div className="text-right">
            <p className="oldstyle font-display text-lg">{trip.reference}</p>
            <p className="mt-0.5 text-[11px] text-gold-soft">
              {trip.arrival_date
                ? `${longDate(trip.arrival_date)} - ${longDate(trip.departure_date)}`
                : "Dates to be confirmed"}
            </p>
          </div>
        </div>
      </header>

      <nav className="no-print border-b border-hairline bg-cream-tint">
        <div className="mx-auto flex max-w-4xl gap-6 px-6">
          {PAGES.map((page) => (
            <Link
              key={page.href}
              href={page.href}
              className={cn(
                "-mb-px border-b-2 py-3 text-[13px]",
                here === page.href
                  ? "border-gold text-ink"
                  : "border-transparent text-ink-soft hover:text-ink",
              )}
            >
              {page.label}
            </Link>
          ))}
        </div>
      </nav>

      <main className="mx-auto max-w-4xl px-6 py-10">{children}</main>

      <Footer />
    </div>
  );
}

function Footer() {
  // "Close" drops the cookie and nothing else. It exists because this is the
  // one page in the platform that gets opened on a hotel's business-centre
  // computer; the client's own link still works afterwards, and nothing is
  // written to the API.
  async function close() {
    await fetch("/api/session", { method: "DELETE" });
    window.location.replace("/trip");
  }

  return (
    <footer className="no-print border-t border-hairline">
      <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-3 px-6 py-8 text-[12px] text-ink-soft">
        <p>
          Everything here is read-only. Any change to your trip goes through
          your consultant.
        </p>
        <button
          type="button"
          onClick={close}
          className="border-b border-hairline pb-0.5 hover:border-gold hover:text-ink"
        >
          Close on a shared computer
        </button>
      </div>
    </footer>
  );
}
