import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MelbProp — Melbourne House Price Predictor",
  description:
    "AI-powered Melbourne property valuations using Random Forest, XGBoost & Linear Regression with an interactive Leaflet map.",
  keywords: "Melbourne, real estate, house price, AI, prediction, property",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        {/* Google Fonts */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Space+Mono:wght@400;700&display=swap"
          rel="stylesheet"
        />
        {/* Leaflet CSS — must be loaded globally */}
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
        />
      </head>
      <body
        style={{ fontFamily: "'Libre Baskerville', Georgia, serif" }}
        className="bg-sand text-charcoal"
      >
        {children}
      </body>
    </html>
  );
}
