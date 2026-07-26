"use client";

import { useEffect, useState } from "react";

/**
 * Pontos de configuração de métricas do motor DRP. Persistidos só no
 * navegador (localStorage) por enquanto — não existe uma tabela de
 * configurações no backend ainda, então isto não é compartilhado entre
 * usuários/sessões. Cada tela usa esses valores como default ao chamar a
 * API, mas a API sempre aceita override pontual por chamada.
 */
export interface ConfiguracaoMetricas {
  nivelServico: number; // 0-1, usado em estoque de segurança (Fase 2)
  custoCompraExterna: number; // penalidade na otimização de rede (Fase 4)
  diasNoMoving: number; // janela para considerar um SKU "sem giro" (Fase 5)
  diasAtrasoCriticoSaneamento: number; // limiar de saneamento de pedidos (Fase 5)
  pesoW1Criticidade: number;
  pesoW2Custo: number;
  pesoW3InversoCobertura: number;
  pesoW4Frequencia: number;
}

export const CONFIG_PADRAO: ConfiguracaoMetricas = {
  nivelServico: 0.95,
  custoCompraExterna: 1000,
  diasNoMoving: 90,
  diasAtrasoCriticoSaneamento: 30,
  pesoW1Criticidade: 0.4,
  pesoW2Custo: 0.2,
  pesoW3InversoCobertura: 0.3,
  pesoW4Frequencia: 0.1,
};

const STORAGE_KEY = "drp-config-metricas";

export function carregarConfiguracao(): ConfiguracaoMetricas {
  if (typeof window === "undefined") return CONFIG_PADRAO;
  try {
    const bruto = window.localStorage.getItem(STORAGE_KEY);
    if (!bruto) return CONFIG_PADRAO;
    return { ...CONFIG_PADRAO, ...JSON.parse(bruto) };
  } catch {
    return CONFIG_PADRAO;
  }
}

export function salvarConfiguracao(config: ConfiguracaoMetricas) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
}

export function useConfiguracao() {
  const [config, setConfig] = useState<ConfiguracaoMetricas>(CONFIG_PADRAO);

  useEffect(() => {
    setConfig(carregarConfiguracao());
  }, []);

  const atualizar = (novo: ConfiguracaoMetricas) => {
    setConfig(novo);
    salvarConfiguracao(novo);
  };

  return { config, atualizar };
}

export function pesosPriorizacao(config: ConfiguracaoMetricas): Record<string, number> {
  return {
    w1: config.pesoW1Criticidade,
    w2: config.pesoW2Custo,
    w3: config.pesoW3InversoCobertura,
    w4: config.pesoW4Frequencia,
  };
}
