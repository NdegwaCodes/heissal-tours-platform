// Reading the public API. Server-side only.
//
// The browser never addresses the API: pages are rendered on the server, the
// enquiry form posts to this app's own route handler, and photographs come
// through /img. That is what lets the API ship with no CORS configuration at
// all (see its public router) -- there is no origin to allow, so there is no
// wildcard to get wrong later.

import type { Contact, Experience, Place, Property } from "@/lib/types";

const API_BASE = process.env.API_BASE_URL ?? "http://localhost:8000";
const V1 = "/api/v1";

// How long a rendered page may be stale. Publishing a property should show up
// without a deploy, and a travel website is not a share price: five minutes is
// invisible to a visitor and takes essentially all the load off the database
// that also runs the quote engine.
export const REVALIDATE = 300;

async function read<T>(path: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${V1}/public/${path}`, {
      next: { revalidate: REVALIDATE },
    });
    if (!res.ok) return fallback;
    return (await res.json()) as T;
  } catch {
    // A page with an empty section is a bad page; a 500 is a lost visitor and
    // a search engine dropping the URL. The lists degrade to empty and the
    // detail pages return null, which the caller turns into a 404.
    return fallback;
  }
}

export const places = () => read<Place[]>("destinations", []);
export const place = (slug: string) =>
  read<Place | null>(`destinations/${encodeURIComponent(slug)}`, null);

export const properties = (destination?: string) =>
  read<Property[]>(
    destination
      ? `accommodations?destination=${encodeURIComponent(destination)}`
      : "accommodations",
    [],
  );
export const property = (slug: string) =>
  read<Property | null>(`accommodations/${encodeURIComponent(slug)}`, null);

export const experiences = (destination?: string) =>
  read<Experience[]>(
    destination
      ? `activities?destination=${encodeURIComponent(destination)}`
      : "activities",
    [],
  );

// A safe placeholder for the one page that must never show a phone number
// nobody would answer: better an unbranded "get in touch" than a fabricated
// one, if the API cannot be reached when this renders.
const NO_CONTACT: Contact = {
  company_name: "Heissal Tours & Travel",
  contact_email: "",
  contact_phone: "",
  social_line: "",
};

export const contact = () => read<Contact>("contact", NO_CONTACT);
