import { WORDMARK, WORDMARK_SUB } from "@/lib/brand";
import type { ApiError } from "@/lib/types";

// A dead link, and which kind of dead.
//
// The heading is chosen from the API's own code and the paragraph is the API's
// own sentence, printed rather than paraphrased. 7.2 wrote three different
// messages on purpose: a client who has cancelled and is told their link
// expired will reasonably conclude the system has lost their booking, and
// "this link no longer works" sends somebody to the telephone with nothing to
// say. Rewriting them here would undo that.
//
// There is no retry and no sign-in offer. Neither is something the client can
// do, and offering an action that cannot work is worse than offering none.
const HEADINGS: Record<string, string> = {
  portal_link_expired: "This link has expired",
  portal_link_revoked: "This link has been withdrawn",
  portal_booking_cancelled: "This booking has been cancelled",
  portal_no_link: "Open your trip from your own link",
};

export function Refused({ error }: { error: ApiError }) {
  const heading = HEADINGS[error.code] ?? "This link does not open a trip";

  return (
    <main className="grid min-h-dvh place-items-center px-6 py-16">
      <div className="max-w-lg">
        <p className="text-[11px] uppercase tracking-eyebrow text-gold">
          {WORDMARK} {WORDMARK_SUB}
        </p>
        <h1 className="mt-4 font-display text-4xl leading-tight">{heading}</h1>
        <p className="mt-5 text-[15px] leading-relaxed text-ink-soft">
          {error.message}
        </p>
      </div>
    </main>
  );
}
