import { Eyebrow } from "@/components/eyebrow";
import { EnquiryForm } from "@/components/enquiry-form";
import { canonical } from "@/lib/site";

export const metadata = {
  title: "Plan a trip",
  description:
    "Tell us when you are travelling, how many of you there are and roughly " +
    "what you want, and a consultant will come back with real options and a price.",
  alternates: { canonical: canonical("/enquire") },
};

export default function Enquire() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-16 sm:py-24">
      <Eyebrow>Plan a trip</Eyebrow>
      <h1 className="mt-3 max-w-2xl font-display text-4xl font-normal leading-[1.1] sm:text-5xl">
        Tell us what you have in mind
      </h1>
      <p className="mt-5 text-[15px] leading-relaxed text-ink-soft">
        There is nothing to sign up for and nothing to pay. A consultant reads
        what you write and answers with properties, a day-by-day and a figure
        for your party &mdash; normally several options, so you are comparing
        rather than agreeing.
      </p>
      <p className="mt-4 text-[14px] leading-relaxed text-ink-soft">
        A name and either an email address or a telephone number is genuinely
        all we need. Dates and numbers help, and &ldquo;August, probably, two of
        us&rdquo; is a perfectly good place to start.
      </p>
      <div className="mt-10">
        <EnquiryForm />
      </div>
    </div>
  );
}
