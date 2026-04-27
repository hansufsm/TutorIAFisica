import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });
const mono = JetBrains_Mono({ subsets: ["latin"] });

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
      <body className={`${inter.className} bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 text-white antialiased overflow-hidden`}>
        <style>{`:root {
          --font-mono: ${mono.style.fontFamily};
        }`}</style>
        {children}
      </body>
    </html>
  );
}
