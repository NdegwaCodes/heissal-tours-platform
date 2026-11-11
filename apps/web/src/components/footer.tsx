import Link from "next/link";
import { contact } from "@/lib/api";

// The footer from the approved Claude Design file, rebuilt with real routes
// -- and, for the phone number and email, real contact details rather than
// the placeholders the design file shipped with. Both are read from the same
// DocumentConfig the quotation document prints (see lib/api.ts:contact), so
// there is exactly one place to update either of them.
const COLS: { head: string; links: { label: string; href: string }[] }[] = [
  {
    head: "Destinations",
    links: [
      { label: "Diani", href: "/destinations" },
      { label: "Watamu", href: "/destinations" },
      { label: "Nanyuki & Mount Kenya", href: "/destinations" },
      { label: "Maasai Mara", href: "/destinations" },
    ],
  },
  {
    head: "Plan",
    links: [
      { label: "Safari builder", href: "/builder" },
      { label: "Itineraries", href: "/destinations" },
      { label: "Gallery", href: "/gallery" },
    ],
  },
  {
    head: "Heissal",
    links: [
      { label: "About", href: "/about" },
      { label: "Contact", href: "/contact" },
      { label: "Enquire", href: "/enquire" },
    ],
  },
];

export async function Footer() {
  const info = await contact();

  return (
    <footer className="border-t border-hairline px-5 py-12 sm:px-8 sm:py-16 lg:px-[88px]">
      <div
        className="mx-auto grid max-w-6xl gap-8 lg:gap-14"
        style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}
      >
        <div>
          <div className="font-display text-[21px] tracking-[0.2em]">HEISSAL</div>
          <div className="mt-1 text-[9px] font-medium tracking-[0.34em] text-gold">
            TOURS · KENYA
          </div>
          <p className="mt-4 max-w-[32ch] text-[14px] leading-relaxed text-ink-soft">
            Tailor-made safaris and coast escapes, built by the people who run
            them.
          </p>
        </div>

        {COLS.map((c) => (
          <div key={c.head} className="flex flex-col gap-2.5">
            <div className="mb-1 text-[11px] font-medium uppercase tracking-eyebrow text-gold">
              {c.head}
            </div>
            {c.links.map((l) => (
              <Link
                key={l.label}
                href={l.href}
                className="text-[15px] text-ink transition hover:text-gold"
              >
                {l.label}
              </Link>
            ))}
          </div>
        ))}

        <div className="flex flex-col gap-2.5">
          <div className="mb-1 text-[11px] font-medium uppercase tracking-eyebrow text-gold">
            Reach us
          </div>
          {info.contact_phone ? (
            <a
              href={`tel:${info.contact_phone.replace(/[^+\d]/g, "")}`}
              className="text-[15px] text-ink transition hover:text-gold"
            >
              {info.contact_phone}
            </a>
          ) : null}
          {info.contact_email ? (
            <a
              href={`mailto:${info.contact_email}`}
              className="text-[15px] text-ink transition hover:text-gold"
            >
              {info.contact_email}
            </a>
          ) : null}
        </div>
      </div>

      <div className="mx-auto mt-12 max-w-6xl border-t border-hairline pt-5 text-[13px] text-ink-soft lg:mt-16">
        &copy; {new Date().getFullYear()} {info.company_name}
      </div>
    </footer>
  );
}
