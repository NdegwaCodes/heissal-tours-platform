import type { Config } from "tailwindcss";
import heissal from "@heissal/brand/tailwind-preset";

// The palette and the type roles come from packages/brand -- one copy, because
// they are the same brand in the quotation document, the client portal and the
// public site, and because the colours are still a guess derived from the
// reference PDF rather than values the client supplied (see
// docs/client-inputs.md). A value expected to change does not belong in three
// files.
//
// The font *files* stay in this app: next/font/local resolves its src paths
// relative to the calling file and needs them inside the app it is building.
// Safe duplication -- the faces are confirmed and a variable font does not get
// edited.
const config: Config = {
  presets: [heissal],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // The premium accent, taken from the brand's own palette rather than
        // invented: the deep Indian-Ocean green (`sea`). It carries the primary
        // CTAs and the active nav pill. Green reads as exclusivity and nature
        // in high-end travel, where a bright orange reads as a discount site.
        // Gold (already in the brand preset, text-gold / text-gold-soft) does
        // the small decorative work: headline accent words and the dots on dark
        // imagery. `ink` is the darker hover, `soft` a pale ground for hover
        // pills. Scoped to the public site so portal and admin are untouched.
        accent: {
          DEFAULT: "#1e4741",
          ink: "#14302b",
          soft: "#e3ede9",
        },
        // A brighter brass than the brand's muted gold, for the primary CTA so
        // it stays legible on the dark hero photograph. Merges into the preset's
        // gold scale, so `bg-gold-bright` sits alongside `text-gold` / `gold-soft`.
        gold: {
          bright: "#c99a3f",
          deep: "#a97f2f",
        },
      },
      borderRadius: {
        pill: "999px",
      },
    },
  },
};

export default config;
