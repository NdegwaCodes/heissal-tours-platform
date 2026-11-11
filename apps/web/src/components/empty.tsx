import Link from "next/link";

// What a section says before anything is published.
//
// Worth writing properly rather than rendering an empty grid: this is exactly
// what the site looks like on the day it goes live, and "nothing here" reads
// as broken while a sentence reads as a business that would rather be asked.
export function Empty({ what }: { what: string }) {
  return (
    <div className="rounded-xl border border-hairline bg-cream-tint px-6 py-8 shadow-sm">
      <p className="text-[14px] leading-relaxed text-ink-soft">
        We are still putting {what} onto the site. In the meantime, tell us
        what you are looking for and a consultant will answer with real
        options.
      </p>
      <Link
        href="/enquire"
        className="mt-4 inline-block border-b border-gold pb-0.5 text-[13px] text-gold"
      >
        Tell us what you have in mind
      </Link>
    </div>
  );
}
