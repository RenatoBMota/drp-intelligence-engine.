import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";

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
        <div className="flex min-h-screen">
          <Nav />
          <main className="flex-1 overflow-x-hidden px-8 py-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
