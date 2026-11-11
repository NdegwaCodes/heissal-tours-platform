import { Redirect } from "@/components/redirect";

// The issued link points at /trip (PortalService.link_for), so this only
// catches somebody who trimmed the URL. It redirects in the browser rather
// than on the server so the fragment survives the hop -- a server redirect
// carrying the client's token would be exactly the thing 7.2 is avoiding,
// and relying on a browser to re-attach a fragment it was never sent is
// relying on a courtesy.
export default function Home() {
  return <Redirect to="/trip" />;
}
