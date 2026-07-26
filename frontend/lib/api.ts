const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

const get = <T>(path: string) => request<T>(path);
const post = <T>(path: string, body: unknown) =>
  request<T>(path, { method: "POST", body: JSON.stringify(body) });
const put = <T>(path: string, body: unknown) =>
  request<T>(path, { method: "PUT", body: JSON.stringify(body) });
const patch = <T>(path: string, body: unknown) =>
  request<T>(path, { method: "PATCH", body: JSON.stringify(body) });

// ---------- Tipos ----------

export interface Sku {
  id: string;
  codigo: string;
  descricao: string;
  unidade_medida: string;
  ativo: boolean;
  fornecedor_id: string | null;
  departamento_id: string | null;
  segmento_id: string | null;
  comprador_id: string | null;
  sku_similar_id: string | null;
  custo_aquisicao: string | null;
  criticidade_resultado: string | null;
  comprabilidade: string | null;
  frequencia_saida: string | null;
  perfil_demanda: string | null;
  lead_time_dias: number | null;
  estoque_seguranca: number | null;
  ponto_pedido: number | null;
  estoque_maximo: number | null;
  cobertura_estoque_manual_dias: number | null;
}

export interface Fornecedor {
  id: string;
  razao_social: string;
  nome_fantasia: string | null;
  cnpj: string;
}

export interface CentroDistribuicao {
  id: string;
  codigo: string;
  nome: string;
}

export interface Filial {
  id: string;
  codigo: string;
  nome: string;
  cd_supridor_id: string | null;
}

export interface SaldoEstoque {
  id: string;
  sku_id: string;
  cd_id: string | null;
  filial_id: string | null;
  quantidade: number;
}

export interface StatusEstoque {
  id: string;
  sku_id: string;
  cd_id: string | null;
  filial_id: string | null;
  necessidade_liquida: number;
  status: string;
  calculado_em: string;
}

export interface OrdemTransferencia {
  id: string;
  sku_id: string;
  origem_cd_id: string | null;
  origem_filial_id: string | null;
  destino_cd_id: string | null;
  destino_filial_id: string | null;
  quantidade: number;
  data_embarque_sugerida: string;
  data_chegada_estimada: string;
  status: string;
  score_criticidade: number;
  justificativa: string;
  data_conclusao: string | null;
}

export interface OrdemCompra {
  id: string;
  sku_id: string;
  fornecedor_id: string;
  destino_cd_id: string | null;
  destino_filial_id: string | null;
  quantidade: number;
  data_solicitacao: string;
  data_previsao: string;
  status: string;
  score_criticidade: number;
  justificativa: string;
  data_conclusao: string | null;
}

export interface Rota {
  id: string;
  origem_cd_id: string | null;
  origem_filial_id: string | null;
  destino_cd_id: string | null;
  destino_filial_id: string | null;
  capacidade_maxima: number;
  custo_unitario: number;
  lead_time_dias: number;
  ativa: boolean;
}

export interface ResumoExecutivo {
  contagem_por_status: Record<string, number>;
  necessidade_liquida_total_aberta: number;
  ordens_transferencia_pendentes: number;
  ordens_compra_pendentes: number;
  taxa_resolucao_rede: {
    quantidade_via_transferencia: number;
    quantidade_via_compra: number;
    taxa_resolucao_rede: number | null;
  };
  lead_time_efetivo: {
    n_ordens_concluidas: number;
    lead_time_planejado_medio_dias: number | null;
    lead_time_efetivo_medio_dias: number | null;
  };
}

export interface ItemPrioridade {
  severidade: string;
  mensagem: string;
}

export interface FluxoAlocado {
  origem: string;
  destino: string;
  quantidade: number;
  custo_unitario: number;
}

export interface ResultadoOtimizacao {
  sucesso: boolean;
  fluxos: FluxoAlocado[];
  custo_total: number;
  quantidade_via_rede: number;
  quantidade_via_compra_externa: number;
  mensagem: string;
}

// ---------- Cadastro ----------

export const api = {
  skus: {
    list: () => get<Sku[]>("/skus"),
    create: (body: Partial<Sku>) => post<Sku>("/skus", body),
    setAtivo: (id: string, ativo: boolean) => patch<Sku>(`/skus/${id}/ativo`, { ativo }),
  },
  fornecedores: {
    list: () => get<Fornecedor[]>("/fornecedores"),
    create: (body: Partial<Fornecedor>) => post<Fornecedor>("/fornecedores", body),
  },
  centrosDistribuicao: {
    list: () => get<CentroDistribuicao[]>("/centros-distribuicao"),
    create: (body: Partial<CentroDistribuicao>) => post<CentroDistribuicao>("/centros-distribuicao", body),
  },
  filiais: {
    list: () => get<Filial[]>("/filiais"),
    create: (body: Partial<Filial>) => post<Filial>("/filiais", body),
  },
  estoque: {
    list: (skuId?: string) => get<SaldoEstoque[]>(`/saldos-estoque${skuId ? `?sku_id=${skuId}` : ""}`),
    set: (body: { sku_id: string; cd_id?: string; filial_id?: string; quantidade: number }) =>
      put<SaldoEstoque>("/saldos-estoque", body),
  },
  drp: {
    recalcular: (body: {
      sku_id: string;
      cd_id?: string;
      filial_id?: string;
      pesos_priorizacao?: Record<string, number>;
    }) =>
      post<{
        status_estoque: StatusEstoque;
        ordem_transferencia: OrdemTransferencia | null;
        ordem_compra: OrdemCompra | null;
        silenciado_motivo: string | null;
      }>("/drp/recalcular", body),
    status: (skuId?: string) => get<StatusEstoque[]>(`/drp/status${skuId ? `?sku_id=${skuId}` : ""}`),
    ordensTransferencia: () => get<OrdemTransferencia[]>("/drp/ordens-transferencia"),
    ordensCompra: () => get<OrdemCompra[]>("/drp/ordens-compra"),
    atualizarOrdemTransferencia: (id: string, status: string, data_conclusao?: string) =>
      patch<OrdemTransferencia>(`/drp/ordens-transferencia/${id}`, { status, data_conclusao }),
    atualizarOrdemCompra: (id: string, status: string, data_conclusao?: string) =>
      patch<OrdemCompra>(`/drp/ordens-compra/${id}`, { status, data_conclusao }),
    alertasDesvio: () => get<OrdemTransferencia[]>("/drp/alertas-desvio"),
  },
  otimizacao: {
    rotas: {
      list: () => get<Rota[]>("/rotas"),
      create: (body: Partial<Rota>) => post<Rota>("/rotas", body),
    },
    otimizar: (skuId: string, custoCompraExterna?: number) =>
      post<ResultadoOtimizacao>(`/otimizacao/sku/${skuId}`, { custo_compra_externa: custoCompraExterna }),
    simular: (
      skuId: string,
      body: { ofertas_override?: Record<string, number>; demandas_override?: Record<string, number>; rotas_desativadas?: string[]; custo_compra_externa?: number }
    ) => post<ResultadoOtimizacao>(`/otimizacao/sku/${skuId}/simular`, body),
  },
  controlTower: {
    resumo: () => get<ResumoExecutivo>("/control-tower/resumo"),
  },
  assistente: {
    resumo: (topN?: number) => get<ItemPrioridade[]>(`/assistente/resumo${topN ? `?top_n=${topN}` : ""}`),
  },
  relatorios: {
    rupturaGeral: () => get<Record<string, number>>("/relatorios/ruptura-geral"),
    coberturaEstoque: () => get<any[]>("/relatorios/cobertura-estoque"),
    pedidosPendentes: () => get<{ transferencias: OrdemTransferencia[]; compras: OrdemCompra[] }>("/relatorios/pedidos-pendentes"),
    otif: () => get<{ n_ordens_concluidas: number; n_no_prazo: number; otif: number | null }>("/relatorios/otif"),
    curvaAbcPqr: () => get<any[]>("/relatorios/curva-abc-pqr"),
    noMoving: (dias?: number) => get<Sku[]>(`/indicadores/no-moving${dias ? `?dias=${dias}` : ""}`),
    exportarUrl: (relatorio: "ruptura-geral" | "pedidos-pendentes") => `${API_URL}/relatorios/${relatorio}/exportar`,
  },
  governanca: {
    saneamento: (diasAtrasoCritico?: number) =>
      get<{ transferencias: OrdemTransferencia[]; compras: OrdemCompra[] }>(
        `/governanca/saneamento${diasAtrasoCritico ? `?dias_atraso_critico=${diasAtrasoCritico}` : ""}`
      ),
  },
};

export { API_URL };
