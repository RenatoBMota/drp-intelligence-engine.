"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const SECOES: { titulo: string; itens: { href: string; label: string }[] }[] = [
  { titulo: "", itens: [{ href: "/", label: "Dashboard" }] },
  {
    titulo: "Cadastro",
    itens: [
      { href: "/cadastro/skus", label: "SKUs" },
      { href: "/cadastro/rede", label: "Rede (CDs / Filiais)" },
      { href: "/cadastro/fornecedores", label: "Fornecedores" },
    ],
  },
  { titulo: "Estoque", itens: [{ href: "/estoque", label: "Saldo por elo" }] },
  {
    titulo: "Motor DRP",
    itens: [
      { href: "/drp/recalcular", label: "Recalcular" },
      { href: "/drp/status", label: "Status de ruptura" },
      { href: "/drp/ordens", label: "Ordens" },
    ],
  },
  {
    titulo: "Otimização",
    itens: [
      { href: "/otimizacao/rotas", label: "Rotas" },
      { href: "/otimizacao/otimizar", label: "Otimizar / Simular" },
    ],
  },
  { titulo: "", itens: [{ href: "/relatorios", label: "Relatórios" }] },
  { titulo: "", itens: [{ href: "/configuracoes", label: "Configurações" }] },
];

export default function Nav() {
  const pathname = usePathname();

  return (
    <nav className="flex w-60 shrink-0 flex-col gap-5 border-r border-slate-800 bg-slate-950 px-4 py-6">
      <Link href="/" className="px-2 text-sm font-semibold tracking-tight text-slate-100">
        DRP Intelligence Engine
      </Link>
      {SECOES.map((secao, i) => (
        <div key={i} className="flex flex-col gap-1">
          {secao.titulo && (
            <span className="px-2 text-xs font-medium uppercase tracking-wide text-slate-500">
              {secao.titulo}
            </span>
          )}
          {secao.itens.map((item) => {
            const ativo = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-md px-2 py-1.5 text-sm transition-colors ${
                  ativo
                    ? "bg-slate-800 text-slate-50"
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      ))}
    </nav>
  );
}
