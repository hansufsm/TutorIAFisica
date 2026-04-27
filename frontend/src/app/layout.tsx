import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Geist } from "next/font/google";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({ subsets: ["latin"], variable: "--font-jakarta" });
const geist = Geist({ subsets: ["latin"], variable: "--font-geist" });

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
    <html lang="pt-BR" className={`${jakarta.variable} ${geist.variable}`}>
      <body className="font-geist bg-white text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}
