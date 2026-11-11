"use client";

import { useState } from "react";
import { Eyebrow } from "@/components/eyebrow";

// The only interactive thing on this site.
//
// It validates nothing beyond what a browser does for free. The rules live in
// the API (app/modules/public/enquiry.py), which refuses only what cannot be
// *answered* -- a name, and one of email or phone -- and its refusal message
// is written to be read by whoever filled the form. A second set of rules here
// would be a second thing to keep in step, and the one that drifted would be
// the one telling somebody their email address is wrong when it is not.
//
// There is no budget field. A figure with no currency beside it is not money,
// and guessing shillings because the site is Kenyan reads a European family's
// 8,000 as a hundredth of what they meant.

type State =
  | { kind: "asking" }
  | { kind: "sending" }
  | { kind: "sent" }
  | { kind: "refused"; message: string };

export function EnquiryForm({ about }: { about?: string }) {
  const [state, setState] = useState<State>({ kind: "asking" });

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setState({ kind: "sending" });

    const value = (name: string) => {
      const raw = form.get(name);
      const text = typeof raw === "string" ? raw.trim() : "";
      return text ? text : null;
    };
    const pax = value("pax");

    const res = await fetch("/api/enquiries", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: value("name") ?? "",
        email: value("email"),
        phone: value("phone"),
        destination: value("destination"),
        travel_from: value("travel_from"),
        travel_to: value("travel_to"),
        pax: pax ? Number(pax) : null,
        message: value("message"),
        // Which page it came from, so a marketing question can be answered
        // with more than "the internet" (5.2 on the source/detail pair).
        page: window.location.pathname,
        trap: value("website_url"),
      }),
    }).catch(() => null);

    if (!res) {
      setState({
        kind: "refused",
        message:
          "That could not be sent just now. Please try again, or telephone us.",
      });
      return;
    }
    if (res.ok) {
      setState({ kind: "sent" });
      return;
    }
    const data = await res.json().catch(() => null);
    setState({
      kind: "refused",
      message:
        data?.error?.message ??
        "That could not be sent just now. Please try again.",
    });
  }

  if (state.kind === "sent") {
    return (
      <div className="rounded-xl border border-hairline bg-cream px-7 py-8 shadow-sm">
        <Eyebrow>Thank you</Eyebrow>
        <p className="mt-3 font-display text-2xl">Your enquiry has reached us</p>
        <p className="mt-3 max-w-lg text-[14px] leading-relaxed text-ink-soft">
          One of our consultants will read it and come back to you. If it is
          urgent, please telephone rather than wait.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="space-y-5">
      {about ? <input type="hidden" name="destination" value={about} /> : null}

      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Your name" name="name" required autoComplete="name" />
        <Field
          label="Email"
          name="email"
          type="email"
          autoComplete="email"
          hint="Email or telephone — either is enough"
        />
        <Field label="Telephone" name="phone" type="tel" autoComplete="tel" />
        {about ? null : (
          <Field
            label="Where you would like to go"
            name="destination"
            hint="If you are not sure yet, leave it"
          />
        )}
      </div>

      <div className="grid gap-5 sm:grid-cols-3">
        <Field label="Travelling from" name="travel_from" type="date" />
        <Field label="Coming back" name="travel_to" type="date" />
        <Field label="How many of you" name="pax" type="number" min={1} />
      </div>

      <label className="block">
        <span className="text-[11px] uppercase tracking-eyebrow text-ink-soft">
          What you have in mind
        </span>
        <textarea
          name="message"
          rows={5}
          className="mt-2 w-full rounded-lg border border-hairline bg-white px-3 py-2 text-[14px] outline-none transition focus:border-gold focus:ring-1 focus:ring-gold/30"
          placeholder="Two of us, somewhere on the coast, sometime in August."
        />
      </label>

      {/*
        The trap. Hidden from people, not from a script -- which is the point.
        Something automated fills every field it finds; a person never sees
        this one. An enquiry that fills it gets the same thank-you and is
        dropped, because telling a bot it failed teaches whoever wrote it which
        field to leave alone next time.
        aria-hidden and tabIndex keep it away from a screen reader and the tab
        order too, so it traps scripts rather than the people this form is for.
      */}
      <div className="hidden" aria-hidden="true">
        <label htmlFor="website_url">Do not fill this in</label>
        <input id="website_url" name="website_url" type="text" tabIndex={-1} />
      </div>

      {state.kind === "refused" ? (
        <p role="alert" className="border-l-2 border-gold pl-4 text-[13px] text-ink">
          {state.message}
        </p>
      ) : null}

      <div className="flex flex-wrap items-center gap-5">
        <button
          type="submit"
          disabled={state.kind === "sending"}
          className="rounded-lg bg-panel px-6 py-3 text-[13px] text-panel-ink transition duration-200 hover:-translate-y-0.5 hover:bg-ink hover:shadow-md disabled:opacity-60"
        >
          {state.kind === "sending" ? "Sending..." : "Send the enquiry"}
        </button>
        <p className="text-[12px] text-ink-soft">
          No account, and nothing to pay. We reply to a person.
        </p>
      </div>
    </form>
  );
}

function Field({
  label,
  name,
  hint,
  ...rest
}: {
  label: string;
  name: string;
  hint?: string;
} & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="block">
      <span className="text-[11px] uppercase tracking-eyebrow text-ink-soft">
        {label}
      </span>
      <input
        name={name}
        {...rest}
        className="mt-2 w-full rounded-lg border border-hairline bg-white px-3 py-2 text-[14px] outline-none transition focus:border-gold focus:ring-1 focus:ring-gold/30"
      />
      {hint ? <span className="mt-1 block text-[11px] text-ink-soft">{hint}</span> : null}
    </label>
  );
}
