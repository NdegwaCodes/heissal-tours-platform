// Structured data, as a script tag.
//
// Only ever built from data the API returned. It is tempting to add ratings,
// review counts and price ranges here because search engines display them --
// and every one of those would be invented, which is both a lie to a visitor
// and, in the case of reviews, against the terms it would be claimed under.
export function JsonLd({ data }: { data: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      // The content is our own object, not user input, and JSON.stringify
      // escapes what matters. The one real hazard is a "</script>" inside a
      // string, which is why the closing angle bracket is escaped.
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data).replace(/</g, "\\u003c"),
      }}
    />
  );
}
