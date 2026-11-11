import { cn } from "@/lib/utils";

// The reference proposal's section label: small, letterspaced, gold. Used the
// same way here so the two documents read as one voice.
export function Eyebrow({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <p
      className={cn(
        "text-[11px] font-medium uppercase tracking-eyebrow text-gold",
        className,
      )}
    >
      {children}
    </p>
  );
}
