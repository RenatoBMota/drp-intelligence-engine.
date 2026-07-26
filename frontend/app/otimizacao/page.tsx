"use client";

import { useState } from "react";
import { PageHeader } from "@/components/ui";
import { TabBar } from "@/components/Tabs";
import RotasPanel from "./_panels/RotasPanel";
import OtimizarPanel from "./_panels/OtimizarPanel";

const TABS = [
  { id: "rotas", label: "Rotas" },
  { id: "otimizar", label: "Otimizar / Simular" },
];

export default function OtimizacaoPage() {
  const [tab, setTab] = useState(TABS[0].id);

  return (
    <div>
      <PageHeader title="Otimização de Rede" subtitle="Rotas de transporte, Programação Linear e simulação de cenários." />
      <TabBar tabs={TABS} active={tab} onChange={setTab} />
      {tab === "rotas" && <RotasPanel />}
      {tab === "otimizar" && <OtimizarPanel />}
    </div>
  );
}
