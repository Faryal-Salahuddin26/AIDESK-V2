import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Providers } from "@/components/providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://aidesk.com'),
  title: {
    default: "AI DESK - Your Window to the Future of AI",
    template: "%s | AI DESK",
  },
  description: "Stay ahead with the latest AI breakthroughs, tools, research, and industry insights. Curated by AI, for the future.",
  keywords: ["AI", "Artificial Intelligence", "Machine Learning", "AI Tools", "AI Research", "AI News", "AI Breakthroughs", "AI Startups"],
  authors: [{ name: "AI DESK" }],
  creator: "AI DESK",
  publisher: "AI DESK",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: process.env.NEXT_PUBLIC_SITE_URL || 'https://aidesk.com',
    siteName: "AI DESK",
    title: "AI DESK - Your Window to the Future of AI",
    description: "Stay ahead with the latest AI breakthroughs, tools, research, and industry insights. Curated by AI, for the future.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "AIDesk",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI DESK - Your Window to the Future of AI",
    description: "Stay ahead with the latest AI breakthroughs, tools, research, and industry insights. Curated by AI, for the future.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: process.env.NEXT_PUBLIC_SITE_URL || 'https://aidesk.com',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning
      >
        <Providers>
          <Header />
          {children}
          <Footer />
        </Providers>
      </body>
    </html>
  );
}

