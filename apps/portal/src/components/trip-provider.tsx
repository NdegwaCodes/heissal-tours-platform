"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { Refused } from "@/components/refused";
import type { ApiError, Trip } from "@/lib/types";

// Opening the trip: the fragment, once, and then never again.
//
// The token arrives in window.location.hash. This does three things with it,
// in this order:
//
//   1. strips it out of the address bar before anything renders, so the URL
//      in a screenshot or a shared screen is not a working link;
//   2. posts it to /api/session, which validates it against the API and puts
//      it in an httpOnly cookie (see src/lib/session.ts);
//   3. renders the trip that came back in the same response.
//
// A reload, or a move to the statement, has no fragment and rides the cookie.
// A client returning next month clicks the link again.

type State =
  | { kind: "opening" }
  | { kind: "open"; trip: Trip }
  | { kind: "refused"; error: ApiError };

const REFUSED_FALLBACK: ApiError = {
  code: "PORTAL_UNAVAILABLE",
  message:
    "Your trip could not be loaded just now. Please try again in a moment -- " +
    "nothing about your booking has changed.",
};

// Memoised at module scope, not in the component. React runs effects twice in
// development, and the second run would find the fragment already stripped
// and race the cookie being set. One promise per page load, shared.
let opening: Promise<State> | null = null;

async function read(res: Response): Promise<State> {
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (res.ok && data) return { kind: "open", trip: data as Trip };
  const error = (data?.error ?? REFUSED_FALLBACK) as ApiError;
  return { kind: "refused", error };
}

async function begin(): Promise<State> {
  const token = window.location.hash.replace(/^#/, "").trim();

  if (token) {
    // Before the request, not after: if the exchange is slow the address bar
    // must already be clean.
    window.history.replaceState(
      null,
      "",
      `${window.location.pathname}${window.location.search}`,
    );
    return read(
      await fetch("/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token }),
      }),
    );
  }

  // No fragment: a reload, an in-app move, or somebody arriving without a
  // link at all. The proxy answers the last case with portal_no_link, which
  // is the sentence the API already wrote for it.
  return read(await fetch("/api/portal/trip"));
}

function open(): Promise<State> {
  if (!opening) {
    opening = begin().catch(
      (): State => ({ kind: "refused", error: REFUSED_FALLBACK }),
    );
  }
  return opening;
}

const Ctx = createContext<Trip | null>(null);

export function useTrip(): Trip {
  const trip = useContext(Ctx);
  if (!trip) throw new Error("useTrip outside a TripProvider");
  return trip;
}

export function TripProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<State>({ kind: "opening" });

  useEffect(() => {
    let live = true;
    open().then((next) => {
      if (live) setState(next);
    });
    return () => {
      live = false;
    };
  }, []);

  if (state.kind === "opening") {
    return (
      <main className="grid min-h-dvh place-items-center px-6">
        <p className="text-sm text-ink-soft">Opening your trip...</p>
      </main>
    );
  }
  if (state.kind === "refused") return <Refused error={state.error} />;

  return <Ctx.Provider value={state.trip}>{children}</Ctx.Provider>;
}
