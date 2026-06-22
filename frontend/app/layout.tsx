import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MelbProp — Melbourne House Price Predictor",
  description: "AI-powered Melbourne property valuations using Random Forest, XGBoost & Linear Regression.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossOrigin="" />
      </head>
      <body style={{ fontFamily: "'Libre Baskerville', Georgia, serif" }}>
        {children}
      </body>
    </html>
  );
}
