"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, ErrorBanner, PageHeader, Table } from "@/components/ui";
import { TabBar } from "@/components/Tabs";
import { useConfiguracao } from "@/lib/config";

const TABS = [
  { id: "ruptura", label: "Ruptura Geral" },
  { id: "otif", label: "OTIF (On Time)" },
  { id: "pendentes", label: "Pedidos Pendentes" },
  { id: "no-moving", label: "Sugestão de Inativação" },
];

export default function RelatoriosPage() {
  const [tab, setTab] = useState(TABS[0].id);
  const [rupturaGeral, setRupturaGeral] = useState<Record<string, number>>({});
  const [otif, setOtif] = useState<{ n_ordens_concluidas: number; n_no_prazo: number; otif: number | null } | null>(null);
  const [pendentes, setPendentes] = useState<{ transferencias: any[]; compras: any[] }>({ transferencias: [], compras: [] });
  const [noMoving, setNoMoving] = useState<any[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const { config } = useConfiguracao();

  useEffect(() => {
    Promise.all([
      api.relatorios.rupturaGeral(),
      api.relatorios.otif(),
      api.relatorios.pedidosPendentes(),
      api.relatorios.noMoving(config.diasNoMoving),
    ])
      .then(([rg, o, pp, nm]) => {
        setRupturaGeral(rg);
        setOtif(o);
        setPendentes(pp);
        setNoMoving(nm);
      })
      .catch((e) => setErro(String(e)));
  }, [config.diasNoMoving]);

  return (
    <div>
      <PageHeader title="Relatórios" subtitle="Indicadores e relatórios herdados do benchmark Systock (Torre de Controle)." />
      <TabBar
        tabs={TABS.map((t) => ({
          ...t,
          badge:
            t.id === "pendentes"
              ? pendentes.transferencias.length + pendentes.compras.length
              : t.id === "no-moving"
              ? noMoving.length
              : undefined,
        }))}
        active={tab}
        onChange={setTab}
      />
      {erro && <ErrorBanner message={erro} />}

      {tab === "ruptura" && (
        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-200">Ruptura Geral</h2>
            <a href={api.relatorios.exportarUrl("ruptura-geral")}>
              <Button variant="secondary">Exportar .xlsx</Button>
            </a>
          </div>
          <Table headers={["Status", "Quantidade"]}>
            {Object.entries(rupturaGeral).map(([status, qtd]) => (
              <tr key={status}>
                <td className="px-3 py-2">{status}</td>
                <td className="px-3 py-2 text-slate-400">{qtd}</td>
              </tr>
            ))}
          </Table>
        </Card>
      )}

      {tab === "otif" && (
        <Card>
          <h2 className="mb-3 text-sm font-semibold text-slate-200">OTIF (On Time)</h2>
          {otif && (
            <div className="flex max-w-sm flex-col gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Ordens concluídas</span>
                <span>{otif.n_ordens_concluidas}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">No prazo</span>
                <span>{otif.n_no_prazo}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">OTIF</span>
                <span className="font-semibold">{otif.otif !== null ? `${(otif.otif * 100).toFixed(0)}%` : "—"}</span>
              </div>
              <p className="text-xs text-slate-500">
                Mede só o &quot;On Time&quot; — o modelo não guarda quantidade recebida separada da solicitada.
              </p>
            </div>
          )}
        </Card>
      )}

      {tab === "pendentes" && (
        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-200">Pedidos Pendentes</h2>
            <a href={api.relatorios.exportarUrl("pedidos-pendentes")}>
              <Button variant="secondary">Exportar .xlsx</Button>
            </a>
          </div>
          <p className="text-sm text-slate-400">
            {pendentes.transferencias.length} transferência(s), {pendentes.compras.length} compra(s) em aberto.
          </p>
        </Card>
      )}

      {tab === "no-moving" && (
        <Card>
          <h2 className="mb-3 text-sm font-semibold text-slate-200">
            Sugestão de Inativação (No Moving — {config.diasNoMoving} dias sem venda)
          </h2>
          <Table headers={["Código", "Descrição"]}>
            {noMoving.map((s) => (
              <tr key={s.id}>
                <td className="px-3 py-2">{s.codigo}</td>
                <td className="px-3 py-2 text-slate-400">{s.descricao}</td>
              </tr>
            ))}
          </Table>
          {noMoving.length === 0 && <p className="text-sm text-slate-500">Nenhum SKU parado no período.</p>}
        </Card>
      )}
    </div>
  );
}
