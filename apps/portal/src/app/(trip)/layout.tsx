import { Chrome } from "@/components/chrome";
import { TripProvider } from "@/components/trip-provider";

// The trip is fetched once, here, for all three pages: the header shows the
// reference on every one of them, and a dead link must be reported before any
// page renders rather than three times over.
export default function TripLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <TripProvider>
      <Chrome>{children}</Chrome>
    </TripProvider>
  );
}
