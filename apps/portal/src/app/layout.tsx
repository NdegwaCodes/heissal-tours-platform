import type { Metadata } from "next";
import "./globals.css";
import { body, display } from "@/lib/fonts";

export const metadata: Metadata = {
  // No trip reference and no client name in the title: a tab title ends up in
  // screenshots, in shared-screen calls, and in whatever the operating system
  // shows on a taskbar.
  title: "Your trip",
  // Says it twice, with the header (next.config.mjs) and the robots route.
  robots: { index: false, follow: false },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      <body className="font-body">{children}</body>
    </html>
  );
}
