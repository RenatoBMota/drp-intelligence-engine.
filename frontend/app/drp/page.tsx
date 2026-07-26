"use client";

import { useState } from "react";
import { PageHeader } from "@/components/ui";
import { TabBar } from "@/components/Tabs";
import RecalcularPanel from "./_panels/RecalcularPanel";
import StatusPanel from "./_panels/StatusPanel";
import OrdensPanel from "./_panels/OrdensPanel";

const TABS = [
  { id: "recalcular", label: "Recalcular" },
  { id: "status", label: "Status de Ruptura" },
  { id: "ordens", label: "Ordens" },
];

export default function DrpPage() {
  const [tab, setTab] = useState(TABS[0].id);

  return (
    <div>
      <PageHeader title="Motor DRP" subtitle="Necessidade líquida, status de ruptura e ordens de ressuprimento." />
      <TabBar tabs={TABS} active={tab} onChange={setTab} />
      {tab === "recalcular" && <RecalcularPanel />}
      {tab === "status" && <StatusPanel />}
      {tab === "ordens" && <OrdensPanel />}
    </div>
  );
}
