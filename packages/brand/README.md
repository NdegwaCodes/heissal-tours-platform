# @heissal/brand

The palette and the type roles, in one place.

## Why this exists

These values started in the quotation document's Jinja template (§3.11), were copied into the
client portal (§7.3), and were about to be copied a third time into the public website (§6.2).
Three was the trigger written down in the portal's own Tailwind config, and it arrived.

The deciding argument is not tidiness. **The palette is a guess.** The ten colours were derived
from the reference proposal PDF rather than supplied by the client, and the real hex
values are still to be confirmed by the client. A value that is expected to change should
not be sitting in three files.

## What is in here, and what is deliberately not

**In:** the colours, the display/body font *roles*, and the eyebrow letter-spacing. Plain
JavaScript with hand-written types rather than TypeScript, because a Tailwind config is loaded
by a different toolchain in each app and a build step here would be a build step three apps
have to wait for.

**Not in: the font files.** `next/font/local` resolves its `src` paths relative to the file that
calls it and needs the files inside the app it is building, so each app keeps its own copy of
the three `.woff2` files. That duplication is safe in a way the palette's was not: the faces are
confirmed (Cormorant Garamond, Libre Franklin), they are used unaltered, and a variable font
file does not get edited.

**Not in: the API's copy.** `apps/api/app/modules/documents/templates/quotation.html.j2` keeps
its own tokens. It is a Python service rendering a print artefact with embedded data-URI fonts
and its own page geometry; making a PDF renderer depend on a Node package to learn a hex code
would be the wrong direction of coupling entirely. When the real palette arrives, two files
change instead of four.

## Using it

```ts
// apps/<app>/tailwind.config.ts
import heissal from "@heissal/brand/tailwind-preset";

export default {
  presets: [heissal],
  content: ["./src/**/*.{ts,tsx}"],
};
```

Both apps declare `--font-display` and `--font-body` themselves, from their own
`next/font/local` call. The preset only says which CSS variable each role reads.
