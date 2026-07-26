"use client";

import { ConfigForm, CampoConfig } from "@/components/ConfigForm";
import { ConfiguracaoMetricas } from "@/lib/config";

const CAMPOS: CampoConfig[] = [
  { chave: "pesoW1Criticidade", label: "Peso w1 — Criticidade de Resultado", step: "0.01", hint: "Fórmula de score: seção 6.5 do roadmap." },
  { chave: "pesoW2Custo", label: "Peso w2 — Custo de Aquisição", step: "0.01", hint: "" },
  { chave: "pesoW3InversoCobertura", label: "Peso w3 — Inverso da Cobertura", step: "0.01", hint: "" },
  { chave: "pesoW4Frequencia", label: "Peso w4 — Frequência de Saída", step: "0.01", hint: "" },
];

export default function PesosPanel({
  config,
  atualizar,
}: {
  config: ConfiguracaoMetricas;
  atualizar: (novo: ConfiguracaoMetricas) => void;
}) {
  return (
    <div>
      <p className="mb-4 text-sm text-slate-400">
        Pesos w1..w4 da fórmula de score de priorização, usados ao recalcular o Motor DRP.
      </p>
      <ConfigForm campos={CAMPOS} config={config} atualizar={atualizar} />
    </div>
  );
}
