import type { Image as ApiImage } from "@/lib/types";
import { imageSrc } from "@/lib/site";
import { cn } from "@/lib/utils";

// A plain <img>, not next/image.
//
// next/image would need the API's image route registered as a remote pattern
// and would then re-fetch and re-encode photographs that /img already serves
// with an immutable cache header. The originals are uploaded through the admin
// at a sensible size and their dimensions come back from the API, so width and
// height are known -- which is the only thing next/image was needed for here
// (it is what stops the page jumping as photographs load).
export function Photo({
  image,
  className,
  priority = false,
  sizes,
}: {
  image: ApiImage;
  className?: string;
  priority?: boolean;
  sizes?: string;
}) {
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={imageSrc(image.url)}
      // Empty rather than a filename or the property name: a decorative
      // photograph with a name repeated from the heading beside it is worse
      // than no alt text for somebody using a screen reader. Real alt text is
      // typed with the upload.
      alt={image.alt_text ?? ""}
      width={image.width ?? undefined}
      height={image.height ?? undefined}
      loading={priority ? "eager" : "lazy"}
      decoding="async"
      sizes={sizes}
      className={cn("block h-full w-full object-cover", className)}
    />
  );
}

export function lead(images: ApiImage[]): ApiImage | null {
  return images.find((one) => one.is_lead) ?? images[0] ?? null;
}
