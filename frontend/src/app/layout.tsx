import type { Metadata } from "next";
import { Inter, Crimson_Text } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });
const crimson = Crimson_Text({ subsets: ["latin"], weight: ["400", "600"], variable: "--font-crimson" });

export const metadata: Metadata = {
  title: "TutorIA Física — UFSM",
  description: "Mentor inteligente para ensino de física universitária",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className={`${inter.className} bg-white text-slate-800 antialiased`}>
        {children}
      </body>
    </html>
  );
}
