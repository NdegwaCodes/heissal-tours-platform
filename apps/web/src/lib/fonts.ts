import { Plus_Jakarta_Sans } from "next/font/google";
import localFont from "next/font/local";

// Display face (3.11), self-hosted from this app: a font request to a third
// party is a request a visitor did not ask to make, and a slow one leaves the
// page set in a fallback at different metrics. Cormorant stays the voice of the
// big headlines — the premium, editorial half of the brand.
export const display = localFont({
  src: [
    { path: "../fonts/cormorant-garamond-normal.woff2", style: "normal" },
    { path: "../fonts/cormorant-garamond-italic.woff2", style: "italic" },
  ],
  variable: "--font-display",
  display: "swap",
  fallback: ["Georgia", "serif"],
});

// The modern UI/body voice: a bold geometric sans for nav, cards, buttons and
// body copy — the contemporary half of the hybrid. `next/font/google` still
// self-hosts (it downloads the files at build time and serves them from this
// app's own origin), so no third-party request reaches a visitor; only the
// build touches Google. Scoped to the public web app; portal/admin keep their
// own body face.
export const body = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-body",
  display: "swap",
  fallback: ["system-ui", "sans-serif"],
});
