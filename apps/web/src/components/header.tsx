import Link from "next/link";

// The header, modernised: the mark on the left, the navigation gathered into a
// floating rounded "pill island" (the travel-app idiom), and a solid accent
// pill for the one action that matters — Enquire. Title Case and the Plus
// Jakarta UI face give it the contemporary feel; the Cormorant wordmark keeps
// the brand's voice.
const NAV: { label: string; href: string }[] = [
  { label: "Itineraries", href: "/destinations" },
  { label: "Destinations", href: "/destinations" },
  { label: "Safari Builder", href: "/builder" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

export function Header() {
  return (
    <header
      className="sticky top-0 z-30 flex flex-wrap items-center justify-between gap-4 px-5 py-4 backdrop-blur sm:px-8 lg:px-[72px]"
      style={{ background: "rgba(253, 251, 246, 0.82)" }}
    >
      <Link href="/" className="flex flex-col gap-0.5 leading-none">
        <span className="font-display text-[23px] tracking-[0.2em]">HEISSAL</span>
        <span className="text-[9px] font-semibold uppercase tracking-[0.34em] text-gold">
          Tours · Kenya
        </span>
      </Link>

      <nav className="flex flex-wrap items-center gap-2">
        <div className="hidden items-center gap-1 rounded-pill border border-hairline bg-white/60 p-1.5 shadow-sm md:flex">
          {NAV.map((n) => (
            <Link
              key={n.label}
              href={n.href}
              className="rounded-pill px-4 py-2 text-[13px] font-medium text-ink transition duration-200 hover:bg-accent-soft hover:text-accent-ink"
            >
              {n.label}
            </Link>
          ))}
        </div>
        <Link
          href="/enquire"
          className="rounded-pill bg-accent px-6 py-2.5 text-[13px] font-semibold text-white shadow-sm transition duration-200 hover:-translate-y-0.5 hover:bg-accent-ink hover:shadow-md"
        >
          Enquire
        </Link>
      </nav>
    </header>
  );
}
