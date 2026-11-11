// The palette. The values below were adopted 2026-09 from the approved public
// website design (Cormorant Garamond + Libre Franklin, in "Heissal Tours
// Website Design"), which resolves the open item on docs/client-inputs.md --
// they are no longer a guess off the reference PDF. Confirm against any
// official brand hex the client later supplies.
//
// Named by role rather than by colour -- `panel` rather than `brown-900` --
// because the names are what the components say, and a rename of a colour
// should not be a rename across three apps.
export const palette = {
  /** Page background. Warm white, not #fff: the reference is printed stock. */
  paper: "#fdfbf6",
  /** Body text. */
  ink: "#1c1a17",
  /** Secondary text, captions, everything that is not the sentence itself. */
  inkSoft: "#6b6558",
  /** The dark blocks -- covers, price panels, the site header band. */
  panel: "#2b211a",
  /** Text on `panel`. */
  panelInk: "#f7f3ec",
  /** Eyebrow labels, rules inside dark panels, links. The warmer brass. */
  gold: "#96703f",
  /** Gold on a dark ground, where the darker one would not carry. */
  goldSoft: "#e4c79a",
  /** The coast accent -- a deep Indian-Ocean green. Used sparingly, against
   *  the gold, to mark the ocean side of the country. */
  sea: "#1e4741",
  /** Sea on a light ground / pale panels that read as water. */
  seaTint: "#dce7e2",
  /** Notice boxes, at-a-glance cells. */
  cream: "#f4eee2",
  /** The lighter fill -- a recommended row, a nav strip. */
  creamTint: "#f8f4ec",
  /** Every rule and border in the system. */
  hairline: "#ded6c6",
};

/** The two brand faces, confirmed 2026-08-25 and used unaltered. */
export const faces = {
  display: "Cormorant Garamond",
  body: "Libre Franklin",
};

/**
 * Fallbacks that matter. A face that fails to load leaves the page set in
 * whatever comes next, so what comes next is named rather than left to the
 * browser's default at different metrics.
 */
export const fallbacks = {
  display: ["Georgia", "serif"],
  body: ["system-ui", "sans-serif"],
};
