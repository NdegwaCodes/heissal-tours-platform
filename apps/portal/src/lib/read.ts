"use client";

import { useEffect, useState } from "react";
import type { ApiError } from "@/lib/types";

// One read, through the proxy. This is all the data-fetching this app needs:
// three GETs and no mutation, because the API it talks to has no write
// endpoint (7.2). The admin's react-query is the right tool for a screen full
// of editable tables; here it would be a dependency strangers load in order
// to fetch one object.

export type Read<T> =
  | { state: "loading" }
  | { state: "ready"; data: T }
  | { state: "failed"; error: ApiError };

const FAILED: ApiError = {
  code: "PORTAL_UNAVAILABLE",
  message:
    "This could not be loaded just now. Please try again in a moment -- " +
    "nothing about your booking has changed.",
};

export function useRead<T>(path: string): Read<T> {
  const [result, setResult] = useState<Read<T>>({ state: "loading" });

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const res = await fetch(`/api/portal/${path}`);
        const text = await res.text();
        const payload = text ? JSON.parse(text) : null;
        if (!live) return;
        if (res.ok && payload) {
          setResult({ state: "ready", data: payload as T });
        } else {
          setResult({
            state: "failed",
            error: (payload?.error ?? FAILED) as ApiError,
          });
        }
      } catch {
        if (live) setResult({ state: "failed", error: FAILED });
      }
    })();
    return () => {
      live = false;
    };
  }, [path]);

  return result;
}
