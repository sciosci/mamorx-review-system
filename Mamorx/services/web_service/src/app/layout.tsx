import type { Metadata } from "next";
import localFont from "next/font/local";
import { Merriweather } from "next/font/google";
import "./globals.css";
import { CSPostHogProvider } from "./providers";
const merriweather = Merriweather({
  subsets: ["latin"],
  weight: ["300", "400", "700", "900"],
  variable: "--font-merriweather",
});

const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "MAMORX - Scientific Review Generation",
  description: "AI-powered scientific review generation system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <CSPostHogProvider>
        <body
          className={`${merriweather.variable} ${geistMono.variable} antialiased`}
        >
          {children}
        </body>
      </CSPostHogProvider>
    </html>
  );
}
