/* eslint-disable @next/next/no-img-element */
// A designed header band for the interior pages: the same dark panel + coast
// photograph + gradient as the home hero, so every page opens the same way.
// The image is the site's own marketing photography from /public, not a
// catalogue image.
import { Eyebrow } from "@/components/eyebrow";

export function PageHeader({
  eyebrow,
  title,
  image,
  children,
}: {
  eyebrow: string;
  title: string;
  image: string;
  children?: React.ReactNode;
}) {
  return (
    <section className="relative isolate overflow-hidden border-b border-hairline bg-panel text-panel-ink">
      <img
        src={image}
        alt=""
        aria-hidden="true"
        className="absolute inset-0 -z-10 h-full w-full object-cover opacity-40"
      />
      <div className="absolute inset-0 -z-10 bg-gradient-to-t from-panel via-panel/85 to-panel/45" />
      <div className="mx-auto max-w-5xl px-6 py-20 sm:py-24">
        <Eyebrow className="text-gold-soft">{eyebrow}</Eyebrow>
        <h1 className="mt-4 max-w-2xl font-display text-4xl leading-[1.06] sm:text-5xl lg:text-6xl">
          {title}
        </h1>
        {children ? (
          <div className="mt-5 max-w-xl text-[15px] leading-relaxed text-gold-soft">
            {children}
          </div>
        ) : null}
      </div>
    </section>
  );
}
