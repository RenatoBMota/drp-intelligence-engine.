"use client";

import { ConfigForm, CampoConfig } from "@/components/ConfigForm";
import { ConfiguracaoMetricas } from "@/lib/config";

const CAMPOS: CampoConfig[] = [
  { chave: "nivelServico", label: "Nível de serviço-alvo (0-1)", step: "0.01", hint: "Usado no estoque de segurança estatístico e Monte Carlo (Fase 2)." },
  { chave: "custoCompraExterna", label: "Custo de compra externa (penalidade)", hint: "Quanto maior, mais o otimizador prefere transferência interna (Fase 4)." },
  { chave: "diasNoMoving", label: "Dias sem venda para 'No Moving'", hint: "Janela usada no relatório de sugestão de inativação (Fase 5)." },
  { chave: "diasAtrasoCriticoSaneamento", label: "Dias de atraso para saneamento", hint: "Pedidos em aberto vencidos há mais que isso entram no saneamento (Fase 5)." },
];

export default function MetricasPanel({
  config,
  atualizar,
}: {
  config: ConfiguracaoMetricas;
  atualizar: (novo: ConfiguracaoMetricas) => void;
}) {
  return (
    <div>
      <p className="mb-4 text-sm text-slate-400">
        Parâmetros gerais usados pelo forecast, otimização e relatórios de governança.
      </p>
      <ConfigForm campos={CAMPOS} config={config} atualizar={atualizar} />
    </div>
  );
}
