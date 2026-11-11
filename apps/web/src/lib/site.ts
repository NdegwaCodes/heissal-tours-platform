// Where this site lives, and how it names itself.

export const SITE_URL = process.env.SITE_URL ?? "http://localhost:3002";

export const SITE_NAME = "Heissal Tours & Travel";

// One sentence, used as the home page description and as the fallback for any
// page without its own. Deliberately says what the business does rather than
// stacking keywords: the second kind reads as spam to a person and, these
// days, to a crawler.
export const SITE_TAGLINE =
  "Tailor-made safaris and coast holidays in Kenya, arranged end to end.";

// The business WhatsApp line for the floating chat button. Digits only, in
// international format, which is what wa.me expects (no +, spaces or dashes).
// This is site contact config, not business pricing — it belongs here beside
// the other site constants, the same way SITE_URL and SITE_NAME do.
export const WHATSAPP_NUMBER = "254758896215";
export const WHATSAPP_URL = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(
  "Hello Heissal Tours, I would like to ask about a safari.",
)}`;

export const canonical = (path: string) => new URL(path, SITE_URL).toString();

// The API hands back image URLs on its own path. They are rewritten onto this
// app's /img so the browser talks only to this origin -- see src/lib/api.ts.
export function imageSrc(url: string): string {
  return url.replace(/^\/api\/v1\/public\/images\//, "/img/");
}
