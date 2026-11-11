import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import { WhatsAppButton } from "@/components/whatsapp-button";
import { body, display } from "@/lib/fonts";
import { SITE_NAME, SITE_TAGLINE, SITE_URL } from "@/lib/site";

export const metadata: Metadata = {
  // metadataBase is what makes every relative canonical, Open Graph URL and
  // sitemap entry resolve to the real domain. Wrong here means wrong in three
  // places that are read by machines and report nothing.
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${SITE_NAME} — safaris and coast holidays in Kenya`,
    // Every page appends the business name, so a tab and a search result both
    // say who this is.
    template: `%s — ${SITE_NAME}`,
  },
  description: SITE_TAGLINE,
  openGraph: {
    siteName: SITE_NAME,
    type: "website",
    locale: "en_KE",
  },
  // The opposite of the portal, which is noindex: this site wants to be found.
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      <body className="flex min-h-dvh flex-col font-body">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
        <WhatsAppButton />
      </body>
    </html>
  );
}
