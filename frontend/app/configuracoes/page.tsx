"use client";

import { FormEvent } from "react";
import { Button, Card, Input, Label, PageHeader } from "@/components/ui";
import { CONFIG_PADRAO, ConfiguracaoMetricas, useConfiguracao } from "@/lib/config";

const CAMPOS: { chave: keyof ConfiguracaoMetricas; label: string; step?: string; hint: string }[] = [
  { chave: "nivelServico", label: "Nível de serviço-alvo (0-1)", step: "0.01", hint: "Usado no estoque de segurança estatístico e Monte Carlo (Fase 2)." },
  { chave: "custoCompraExterna", label: "Custo de compra externa (penalidade)", hint: "Quanto maior, mais o otimizador prefere transferência interna (Fase 4)." },
  { chave: "diasNoMoving", label: "Dias sem venda para 'No Moving'", hint: "Janela usada no relatório de sugestão de inativação (Fase 5)." },
  { chave: "diasAtrasoCriticoSaneamento", label: "Dias de atraso para saneamento", hint: "Pedidos em aberto vencidos há mais que isso entram no saneamento (Fase 5)." },
  { chave: "pesoW1Criticidade", label: "Peso w1 — Criticidade de Resultado", step: "0.01", hint: "Fórmula de score: seção 6.5 do roadmap." },
  { chave: "pesoW2Custo", label: "Peso w2 — Custo de Aquisição", step: "0.01", hint: "" },
  { chave: "pesoW3InversoCobertura", label: "Peso w3 — Inverso da Cobertura", step: "0.01", hint: "" },
  { chave: "pesoW4Frequencia", label: "Peso w4 — Frequência de Saída", step: "0.01", hint: "" },
];

export default function ConfiguracoesPage() {
  const { config, atualizar } = useConfiguracao();

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const novo = { ...config };
    for (const campo of CAMPOS) {
      (novo[campo.chave] as number) = Number(form.get(campo.chave));
    }
    atualizar(novo);
  };

  const restaurarPadrao = () => atualizar(CONFIG_PADRAO);

  return (
    <div>
      <PageHeader
        title="Configurações"
        subtitle="Pontos de configuração das métricas do motor DRP. Salvo no navegador (localStorage) — ainda não há uma tabela de configurações persistida no backend; cada tela envia esses valores como parâmetro em cada chamada de API."
      />

      <Card>
        <form onSubmit={onSubmit} className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {CAMPOS.map((campo) => (
            <div key={campo.chave} className="flex flex-col gap-1">
              <Label>{campo.label}</Label>
              <Input name={campo.chave} type="number" step={campo.step ?? "1"} defaultValue={config[campo.chave]} />
              {campo.hint && <span className="text-xs text-slate-500">{campo.hint}</span>}
            </div>
          ))}

          <div className="flex gap-2 md:col-span-2">
            <Button type="submit">Salvar configuração</Button>
            <Button type="button" variant="secondary" onClick={restaurarPadrao}>
              Restaurar padrão
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
