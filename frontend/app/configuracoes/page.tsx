"use client";

import { useState } from "react";
import { PageHeader } from "@/components/ui";
import { TabBar } from "@/components/Tabs";
import { useConfiguracao } from "@/lib/config";
import MetricasPanel from "./_panels/MetricasPanel";
import PesosPanel from "./_panels/PesosPanel";

const TABS = [
  { id: "metricas", label: "Métricas Gerais" },
  { id: "pesos", label: "Pesos de Priorização" },
];

export default function ConfiguracoesPage() {
  const [tab, setTab] = useState(TABS[0].id);
  const { config, atualizar } = useConfiguracao();

  return (
    <div>
      <PageHeader
        title="Configurações"
        subtitle="Pontos de configuração das métricas do motor DRP. Salvo no navegador (localStorage) — ainda não há uma tabela de configurações persistida no backend; cada tela envia esses valores como parâmetro em cada chamada de API."
      />
      <TabBar tabs={TABS} active={tab} onChange={setTab} />
      {tab === "metricas" && <MetricasPanel config={config} atualizar={atualizar} />}
      {tab === "pesos" && <PesosPanel config={config} atualizar={atualizar} />}
    </div>
  );
}
