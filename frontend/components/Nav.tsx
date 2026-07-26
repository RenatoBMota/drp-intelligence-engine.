"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentType } from "react";
import {
  IconCadastro,
  IconConfig,
  IconDashboard,
  IconEstoque,
  IconMotor,
  IconOtimizacao,
  IconRelatorios,
} from "@/components/icons";

const ITENS: { href: string; label: string; icon: ComponentType<{ className?: string }> }[] = [
  { href: "/", label: "Dashboard", icon: IconDashboard },
  { href: "/cadastro", label: "Cadastro", icon: IconCadastro },
  { href: "/estoque", label: "Estoque", icon: IconEstoque },
  { href: "/drp", label: "Motor DRP", icon: IconMotor },
  { href: "/otimizacao", label: "Otimização", icon: IconOtimizacao },
  { href: "/relatorios", label: "Relatórios", icon: IconRelatorios },
  { href: "/configuracoes", label: "Configurações", icon: IconConfig },
];

export default function Nav() {
  const pathname = usePathname();

  return (
    <nav className="flex w-60 shrink-0 flex-col gap-1 border-r border-slate-800 bg-slate-950 px-3 py-6">
      <Link href="/" className="mb-5 flex items-center gap-2 px-2 text-sm font-semibold tracking-tight text-slate-100">
        <span className="flex h-6 w-6 items-center justify-center rounded-md bg-sky-500/15 text-xs font-bold text-sky-400">
          D
        </span>
        DRP Intelligence Engine
      </Link>
      {ITENS.map((item) => {
        const ativo = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`group flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition-colors ${
              ativo
                ? "bg-sky-500/10 text-sky-300"
                : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
            }`}
          >
            <Icon
              className={`h-4 w-4 shrink-0 ${ativo ? "text-sky-400" : "text-slate-500 group-hover:text-slate-300"}`}
            />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
