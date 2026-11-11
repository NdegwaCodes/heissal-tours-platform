import { canonical } from "@/lib/site";
import DestinationsView from "./view";

export const metadata = {
  title: "Destinations",
  description:
    "Trips we run across the Kenyan coast and highlands — real routes, real properties, " +
    "prices shown where the rate data is complete.",
  alternates: { canonical: canonical("/destinations") },
};

export default function Destinations() {
  return <DestinationsView />;
}
