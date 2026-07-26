"use client";

import { useEffect, useState } from "react";
import { api, ItemPrioridade, ResumoExecutivo } from "@/lib/api";
import { Badge, Card, ErrorBanner, PageHeader, StatTile } from "@/components/ui";

const SEVERIDADE_TONE: Record<string, "danger" | "warning" | "neutral"> = {
  CRITICA: "danger",
  ALTA: "warning",
  MEDIA: "neutral",
};

export default function DashboardPage() {
  const [resumo, setResumo] = useState<ResumoExecutivo | null>(null);
  const [prioridades, setPrioridades] = useState<ItemPrioridade[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    Promise.all([api.controlTower.resumo(), api.assistente.resumo(10)])
      .then(([r, p]) => {
        setResumo(r);
        setPrioridades(p);
      })
      .catch((e) => setErro(String(e)))
      .finally(() => setCarregando(false));
  }, []);

  return (
    <div>
      <PageHeader
        title="Torre de Controle"
        subtitle="Visão executiva da rede — status por elo, KPIs e prioridades do assistente."
      />

      {erro && <ErrorBanner message={erro} />}
      {carregando && <p className="text-sm text-slate-500">Carregando...</p>}

      {resumo && (
        <>
          <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
            <StatTile
              label="Necessidade líquida em aberto"
              value={resumo.necessidade_liquida_total_aberta.toFixed(1)}
            />
            <StatTile label="Ordens de transferência pendentes" value={resumo.ordens_transferencia_pendentes} />
            <StatTile label="Ordens de compra pendentes" value={resumo.ordens_compra_pendentes} />
            <StatTile
              label="Taxa de resolução por rede"
              value={
                resumo.taxa_resolucao_rede.taxa_resolucao_rede !== null
                  ? `${(resumo.taxa_resolucao_rede.taxa_resolucao_rede * 100).toFixed(0)}%`
                  : "—"
              }
              hint="% resolvido via transferência interna vs. compra"
            />
          </div>

          <div className="mb-6 grid gap-4 md:grid-cols-2">
            <Card>
              <h2 className="mb-3 text-sm font-semibold text-slate-200">Elos por status</h2>
              <div className="flex flex-col gap-2">
                {Object.entries(resumo.contagem_por_status).map(([status, qtd]) => (
                  <div key={status} className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">{status}</span>
                    <span className="font-medium text-slate-100">{qtd}</span>
                  </div>
                ))}
                {Object.keys(resumo.contagem_por_status).length === 0 && (
                  <p className="text-sm text-slate-500">Nenhum status calculado ainda.</p>
                )}
              </div>
            </Card>

            <Card>
              <h2 className="mb-3 text-sm font-semibold text-slate-200">Lead Time Efetivo vs. Planejado</h2>
              <div className="flex flex-col gap-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Ordens concluídas consideradas</span>
                  <span>{resumo.lead_time_efetivo.n_ordens_concluidas}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Planejado (média)</span>
                  <span>{resumo.lead_time_efetivo.lead_time_planejado_medio_dias?.toFixed(1) ?? "—"} dias</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Efetivo (média)</span>
                  <span>{resumo.lead_time_efetivo.lead_time_efetivo_medio_dias?.toFixed(1) ?? "—"} dias</span>
                </div>
              </div>
            </Card>
          </div>
        </>
      )}

      <Card>
        <h2 className="mb-3 text-sm font-semibold text-slate-200">
          Assistente de prioridades <span className="text-slate-500">(RBM TASK 2.0 — baseado em regras)</span>
        </h2>
        <div className="flex flex-col gap-2">
          {prioridades.map((item, i) => (
            <div key={i} className="flex items-start gap-2 text-sm">
              <Badge tone={SEVERIDADE_TONE[item.severidade] ?? "neutral"}>{item.severidade}</Badge>
              <span className="text-slate-300">{item.mensagem}</span>
            </div>
          ))}
          {prioridades.length === 0 && !carregando && (
            <p className="text-sm text-slate-500">Nenhuma prioridade no momento.</p>
          )}
        </div>
      </Card>
    </div>
  );
}
