import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const font = Inter({ subsets: ["latin"] });

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
      <body className={`${font.className} bg-gray-950 text-white antialiased`}>
        {children}
      </body>
    </html>
  );
}
