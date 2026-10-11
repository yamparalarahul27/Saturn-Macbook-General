import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "INS Vikramaditya · Paper Craft",
  description:
    "Build a paper INS Vikramaditya with five printable A4 sheets and a step-by-step cut, fold, and glue guide.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
