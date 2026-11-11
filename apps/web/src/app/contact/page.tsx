import Link from "next/link";
import { contact } from "@/lib/api";
import { canonical } from "@/lib/site";

export const metadata = {
  title: "Contact",
  description:
    "Talk to a person at Heissal Tours — phone and WhatsApp, email, or an " +
    "enquiry that comes straight to the people who run the trips.",
  alternates: { canonical: canonical("/contact") },
};

const EYE = "text-[11px] font-medium uppercase tracking-eyebrow text-gold";

export default async function Contact() {
  // Read from the same DocumentConfig the quotation document prints, rather
  // than typed a second time here -- a phone number on this page and a
  // different one on a client's proposal is exactly the kind of drift a
  // second copy invites.
  const info = await contact();

  return (
    <section className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
      <p className={EYE}>Contact</p>
      <h1 className="mt-3 max-w-2xl font-display text-4xl font-normal leading-[1.06] sm:text-5xl lg:text-6xl">
        Talk to a person
      </h1>
      <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-ink-soft">
        No call centre and no ticket queue. Whichever way you reach us, you get
        the small team who plan and host the trips — usually the same day, East
        Africa time.
      </p>

      <div className="mt-12 grid gap-x-8 gap-y-12 border-t border-hairline pt-12 sm:grid-cols-3">
        <div>
          <p className={EYE}>Phone &amp; WhatsApp</p>
          {info.contact_phone ? (
            <a
              href={`tel:${info.contact_phone.replace(/[^+\d]/g, "")}`}
              className="mt-3 block font-display text-2xl transition hover:text-gold"
            >
              {info.contact_phone}
            </a>
          ) : (
            <p className="mt-3 text-[14px] text-ink-soft">
              Use the enquiry form below and we will call you.
            </p>
          )}
          <p className="mt-3 text-[14px] leading-relaxed text-ink-soft">
            Best for a quick question or to talk a route through. WhatsApp is on
            the same number.
          </p>
        </div>

        <div>
          <p className={EYE}>Email</p>
          {info.contact_email ? (
            <a
              href={`mailto:${info.contact_email}`}
              className="mt-3 block font-display text-2xl transition hover:text-gold"
            >
              {info.contact_email}
            </a>
          ) : (
            <p className="mt-3 text-[14px] text-ink-soft">
              Use the enquiry form below and we will reply by email.
            </p>
          )}
          <p className="mt-3 text-[14px] leading-relaxed text-ink-soft">
            Best for dates, numbers and anything you would rather write down.
            We reply with a real person, not a template.
          </p>
        </div>

        <div>
          <p className={EYE}>Travel agents</p>
          <p className="mt-3 font-display text-2xl">Trade &amp; groups</p>
          <p className="mt-3 text-[14px] leading-relaxed text-ink-soft">
            We work with agents on net rates and with families and small groups
            on private departures. Say so in your enquiry and we will set it up.
          </p>
        </div>
      </div>

      <div className="mt-14 border-t border-hairline pt-12">
        <p className="max-w-xl text-[15px] leading-relaxed text-ink-soft">
          Prefer to lay it all out at once? The enquiry form carries your dates,
          party and anything you have built so far.
        </p>
        <Link
          href="/enquire"
          className="mt-6 inline-block rounded-lg bg-ink px-7 py-4 text-[12px] font-medium uppercase tracking-[0.13em] text-[#f7f3ec] transition duration-200 hover:-translate-y-0.5 hover:bg-panel hover:shadow-md"
        >
          Start an enquiry
        </Link>
      </div>
    </section>
  );
}
