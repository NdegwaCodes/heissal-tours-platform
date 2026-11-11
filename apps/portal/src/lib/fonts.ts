import localFont from "next/font/local";

// The brand faces (3.11), served from this app rather than from Google.
//
// Local for the same two reasons the quotation document embeds them: a
// network font request that fails leaves the page set in a fallback at
// different metrics with no error raised, and a client opening their
// itinerary should not have their visit announced to a third party.
//
// Both are variable, so one file covers the weight range.
export const display = localFont({
  src: [
    { path: "../fonts/cormorant-garamond-normal.woff2", style: "normal" },
    { path: "../fonts/cormorant-garamond-italic.woff2", style: "italic" },
  ],
  variable: "--font-display",
  display: "swap",
  fallback: ["Georgia", "serif"],
});

export const body = localFont({
  src: [{ path: "../fonts/libre-franklin-normal.woff2", style: "normal" }],
  variable: "--font-body",
  display: "swap",
  fallback: ["system-ui", "sans-serif"],
});
