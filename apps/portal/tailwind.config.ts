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
};

export default config;
