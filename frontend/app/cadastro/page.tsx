"use client";

import { useState } from "react";
import { PageHeader } from "@/components/ui";
import { TabBar } from "@/components/Tabs";
import SkusPanel from "./_panels/SkusPanel";
import RedePanel from "./_panels/RedePanel";
import FornecedoresPanel from "./_panels/FornecedoresPanel";

const TABS = [
  { id: "skus", label: "SKUs" },
  { id: "rede", label: "Rede (CDs / Filiais)" },
  { id: "fornecedores", label: "Fornecedores" },
];

export default function CadastroPage() {
  const [tab, setTab] = useState(TABS[0].id);

  return (
    <div>
      <PageHeader title="Cadastro" subtitle="Os cadastros base que o Motor DRP consulta em todo o fluxo." />
      <TabBar tabs={TABS} active={tab} onChange={setTab} />
      {tab === "skus" && <SkusPanel />}
      {tab === "rede" && <RedePanel />}
      {tab === "fornecedores" && <FornecedoresPanel />}
    </div>
  );
}
