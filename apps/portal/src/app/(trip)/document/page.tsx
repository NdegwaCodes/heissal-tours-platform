"use client";

import { Eyebrow } from "@/components/eyebrow";
import { useTrip } from "@/components/trip-provider";

// The proposal they accepted, exactly as it was issued.
//
// Rendered by the API from the frozen version pinned to the booking (7.2), so
// a client re-opening it in March sees what they agreed to in September and
// not a re-render of a quote that has been edited since.
//
// It comes through in an iframe rather than being re-implemented in React.
// The document is a print artefact with its own page geometry, its own
// embedded faces and its own two hundred lines of CSS (3.11); a second
// rendering of it in this app would be a second thing to keep in step, and
// the copy the client agreed to is the one the renderer produces.

export default function DocumentPage() {
  const trip = useTrip();

  return (
    <div className="space-y-6">
      <div className="no-print">
        <Eyebrow>Your proposal</Eyebrow>
        <h1 className="mt-3 font-display text-3xl">
          The document you accepted
        </h1>
        <p className="mt-3 max-w-xl text-[13px] leading-relaxed text-ink-soft">
          Exactly as it was sent to you, for {trip.reference}. It does not
          change when our prices do.
        </p>
      </div>

      <iframe
        // A same-origin frame, so the proxy's cookie reaches it; the API is
        // never addressed by the browser directly.
        src="/api/portal/document.html"
        title="Your proposal"
        className="h-[80vh] w-full border border-hairline bg-white"
      />

      <p className="no-print text-[12px] text-ink-soft">
        To keep a copy, use your browser&apos;s print or save-as-PDF from inside the
        document above.
      </p>
    </div>
  );
}
