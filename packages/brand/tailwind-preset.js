import { fallbacks, palette } from "./index.js";

// A Tailwind preset rather than a config: an app still owns its own `content`
// globs, its plugins and anything it adds. This says only what the brand is.
//
// The nested shape (`ink.DEFAULT` / `ink.soft`) is what makes `text-ink` and
// `text-ink-soft` both work, which is how the components already read.
const preset = {
  theme: {
    extend: {
      colors: {
        paper: palette.paper,
        ink: { DEFAULT: palette.ink, soft: palette.inkSoft },
        panel: { DEFAULT: palette.panel, ink: palette.panelInk },
        gold: { DEFAULT: palette.gold, soft: palette.goldSoft },
        sea: { DEFAULT: palette.sea, tint: palette.seaTint },
        cream: { DEFAULT: palette.cream, tint: palette.creamTint },
        hairline: palette.hairline,
      },
      fontFamily: {
        // The variable is set by each app's own next/font/local call -- the
        // font files stay in the app (see README). This only fixes which
        // variable each role reads and what happens if it is not there.
        display: ["var(--font-display)", ...fallbacks.display],
        body: ["var(--font-body)", ...fallbacks.body],
      },
      letterSpacing: {
        // The reference proposal's section labels. Wide enough to read as a
        // label rather than as small text.
        eyebrow: "0.14em",
      },
    },
  },
};

export default preset;
