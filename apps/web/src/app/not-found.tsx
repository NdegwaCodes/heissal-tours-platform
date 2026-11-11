import Link from "next/link";
import { Eyebrow } from "@/components/eyebrow";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl px-6 py-24">
      <Eyebrow>Not found</Eyebrow>
      <h1 className="mt-3 font-display text-4xl">
        This page is not here any more
      </h1>
      <p className="mt-4 text-[15px] leading-relaxed text-ink-soft">
        It may have been a property or a destination we no longer offer. Our
        current destinations are below, and if you were looking for something
        in particular we would rather you asked than gave up.
      </p>
      <div className="mt-8 flex flex-wrap gap-6 text-[13px]">
        <Link href="/destinations" className="border-b border-gold pb-0.5 text-gold">
          Destinations
        </Link>
        <Link href="/enquire" className="border-b border-gold pb-0.5 text-gold">
          Ask us
        </Link>
      </div>
    </div>
  );
}
