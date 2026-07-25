import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DRP Intelligence Engine",
  description: "Planejamento de distribuição, forecast e otimização de rede.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="bg-slate-950 text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
