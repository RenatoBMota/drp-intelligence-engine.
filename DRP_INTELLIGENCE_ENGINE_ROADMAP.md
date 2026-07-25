# DRP Intelligence Engine — Documento Estrutural do Projeto
**Versão 1.0 — Baseado no documento inicial + benchmark funcional Systock**

> Este documento consolida (1) a visão inicial do `Projeto_DRP_Intelligence_Engine_v1.docx` e (2) o levantamento funcional completo do manual "Jornada Systock", usado como benchmark de mercado para o motor de DRP. O objetivo é sair de um esqueleto de tópicos genéricos para uma estrutura de projeto acionável, com foco central em DRP (Distribution Requirements Planning).

---

## Sumário

1. Visão Geral do Produto
2. Objetivos Estratégicos e Métricas de Sucesso
3. Fundamentos Conceituais de DRP
4. Benchmark Funcional — Systock (mapeamento completo)
5. Arquitetura da Solução
6. Motor DRP — Especificação Detalhada
7. Modelos Matemáticos e Estatísticos
8. Modelo de Dados
9. APIs e Integrações
10. Dashboards, Indicadores e Relatórios
11. Regras de Governança, Saneamento e Auditoria
12. Roadmap de Entrega
13. Riscos e Pontos em Aberto

---

## 1. Visão Geral do Produto

Plataforma corporativa de **planejamento de distribuição** (DRP), otimização de estoques, forecast, simulação, inteligência artificial e pesquisa operacional, voltada a redes varejistas, home centers, distribuidores e indústrias com múltiplos CDs e filiais.

O núcleo do produto é o **Motor DRP**: dado o histórico de demanda, a rede logística (CD → Filiais) e as regras de reposição, o motor decide *o quê*, *quanto*, *de onde* e *quando* transferir ou comprar, priorizando pelos SKUs de maior criticidade e risco de ruptura.

Diferente de um sistema de compras tradicional (ponto de pedido simples), o DRP trabalha em rede: ele enxerga o estoque em todos os elos (CD e lojas) e otimiza a redistribuição entre eles antes de gerar uma nova ordem de compra externa.

---

## 2. Objetivos Estratégicos e Métricas de Sucesso

| Objetivo | Métrica (KPI) | Fonte de referência |
|---|---|---|
| Reduzir ruptura | % Ruptura, Perda de Venda por Ruptura | Gráfico "Ruptura por Compra x Ruptura por DRP" (Systock) |
| Reduzir excesso de estoque | Produtos em Excesso, Estoque Acima do Emáx | Análise por Fornecedores/Departamentos |
| Reduzir capital empatado | Total Estoque Atual (R$), Cobertura de Estoque | Dashboard, Detalhes do Produto |
| Aumentar giro | Giro de Estoque, Cobertura Instantânea | Raio-X do Produto |
| Aumentar nível de serviço | OTIF, Fill Rate | Indicador OTIF (Relatórios) |
| Melhorar eficiência de compra | Eficiência do Comprador (%), Qualidade do Estoque | Análise por Compradores |
| Reduzir custo logístico | Saving de Compras | Relatórios Systock |

---

## 3. Fundamentos Conceituais de DRP

DRP (Distribution Requirements Planning) é a extensão em rede do MRP (Material Requirements Planning) aplicada à distribuição: em vez de planejar apenas a reposição de um ponto de estoque isolado, o DRP:

- Consolida a demanda de todas as filiais atendidas por um CD ("necessidade líquida agregada");
- Calcula o momento ótimo de disparo considerando **lead time**, **estoque de segurança** e **cobertura**;
- Decide entre **redistribuição interna** (transferência entre filiais/CD) e **ressuprimento externo** (compra ao fornecedor);
- Gera **ordens de transferência** priorizadas por criticidade, e não apenas por ordem de cadastro;
- Opera de forma contínua (rolling horizon), recalculando a cada nova informação de venda, entrada ou trânsito.

### 3.1 Diferença central: Ruptura por Compra vs. Ruptura por DRP

O manual do Systock já materializa esse conceito de forma simples e é a base conceitual que o motor deve herdar e sofisticar:

- **Ruptura por Compra**: o saldo de estoque está abaixo do estoque de segurança — típico de uma lógica de reposição local, sem visão de rede.
- **Ruptura por DRP**: mesmo havendo saldo, o sistema aponta ruptura porque a rede (CD) está acima do estoque de segurança mas incapaz de suprir a demanda projetada das pontas dentro do lead time — ou seja, a ruptura é *prevista pela rede*, não apenas pelo saldo local.

Essa distinção deve ser um cidadão de primeira classe no modelo de dados (campo `tipo_ruptura: COMPRA | DRP`) e nos dashboards, não apenas uma cor de gráfico.

---

## 4. Benchmark Funcional — Systock (mapeamento completo)

Levantamento extraído do manual "Jornada Systock" (45 telas), organizado por domínio funcional. Serve como *baseline* de paridade mínima do DRP Intelligence Engine.

### 4.1 Acesso e Estrutura Geral
- Login / recuperação de senha.
- Menu lateral: Dashboard, Controle de Acesso, Compras, Configurações do Sistema, Produção, Indicadores, Logística, Relatórios.
- Dashboard: gráfico anual Compras (azul claro) vs. Entradas com NF (azul escuro) vs. Saídas/Vendas (vermelho), segmentado por **Grupo de Compras**.

### 4.2 Grupos de Compras
- Agrupamento lógico de fornecedores/filiais para análise e compra conjunta.
- Criação de "grupo de análise" nomeado, agregando fornecedores selecionados.
- Ao mandar para o carrinho, o sistema abre **um pedido por fornecedor** dentro do grupo — a menos que se use **Consolidar Carrinhos**, que funde tudo em um único arquivo/pedido consolidado.

### 4.3 Análise por Fornecedores
Camada de análise quantitativa por fornecedor, com sub-relatórios exportáveis:
- Qtde. Produtos Total
- Produtos em Excesso (acima do estoque máximo)
- Produtos Adequado (dentro da faixa ponto de pedido–máximo)
- Produtos a Comprar (abaixo do ponto de pedido, com tipo de compra e status)
- Produtos em Trânsito (detalhe por item, com estoque de segurança, ponto de pedido, estoque máximo, cobertura, consumo médio mensal)

### 4.4 Análise por Departamentos / Segmentos
- Visão agregada por departamento (ex: Embutidos, Aves) e por segmento (ex: Peças para Máquinas, Material Elétrico), com margem, projeção de venda, estoque em loja/CD, cobertura loja/CD/geral e **sugestão de compra**.
- Drill-down "Estoque por loja": quantitativo (projeção, saldo, cobertura, saldo ideal, diferença %) e financeiro (projeção/estoque a preço de custo e de venda) por loja individual — essencial para o motor DRP multi-filial.
- Lista de Segmentos em Ressuprimento: por fornecedor, quem é o comprador responsável, dias em cotação, produtos OK vs. a ressuprir vs. em trânsito.

### 4.5 Pedidos em Trânsito
- Lista de pedidos com data de solicitação, previsão de chegada, código do fornecedor, quantidade de itens/pendentes e valor total.
- Detalhe do pedido item a item (quantidade solicitada, entregue, pendente).

### 4.6 Análise de Produtos e Detalhamento do Produto
Ficha completa de SKU — é o núcleo de dados que o motor de cálculo consome:

| Campo | Definição |
|---|---|
| Custo de Aquisição | Elevado / Intermediário / Baixo — classificação de importância financeira |
| Criticidade de Resultado | Vital / Intermediário / Ordinário — importância no faturamento |
| Comprabilidade | Complexo / Difícil / Previsível — confiabilidade de prazo/fornecedor |
| Frequência de Saída | Popular / Intermediária / Raro |
| Perfil de Demanda | Repetitivo, etc. — comportamento da série temporal |
| Ressuprimento (Lead Time) | Prazo total da necessidade até o recebimento |
| Estoque de Segurança | Estoque mínimo para mitigar stockout |
| Ponto de Pedido | Gatilho de disparo de compra/transferência |
| Estoque Máximo | Teto de estoque para o SKU |
| Nível de Estoque (%) | Saldo atual frente a máximo/segurança |
| Cobertura de Estoque (dias) | Tempo que o saldo cobre a demanda futura |
| Projeção de Venda | Previsão baseada em histórico (3/6/12 meses) |
| Desvio Padrão / Coeficiente de Variação | Medidas de incerteza da demanda |
| Similares / Herança | Produtos que herdam comportamento de outro item (para itens novos sem histórico) |
| Influenciar Projeção | Ajuste manual (%) por período, com data limite e escopo (item/fornecedor) |
| Cobertura de Estoque Manual | Override manual da cobertura calculada automaticamente |

- **Raio-X do Produto**: gráfico consolidado (Estoque, Saídas, Entradas, Estoque de Segurança, Ponto de Pedido, Estoque Máximo, Projeção de Venda) por período (1/2/3/6/9 meses, 1 ano, consolidado), com painel lateral de "Caracterização do Item" e "Estatísticas Apuradas" (Esseg, PP, Emáx, CM — limites superior/inferior, amplitude) e classificação por faixas: **Saldo Acima do Emáx, Saldo Adequado, Saldo Exposto a Ruptura, Saldo em Ruptura** — com dias e % de "espaço amostral" em cada faixa.

### 4.7 Simbologias e Gatilhos
- **Dias de Gatilho**: contagem regressiva/progressiva de dias até a compra recomendada.
- **Sugestão de Compra**: gerada por análise estatística multivariável.
- **Cobertura de Estoque Futura**: projeção de quanto tempo o estoque restante cobrirá a demanda.

### 4.8 Carrinho de Compras / Fluxo de Compra
- Itens a Comprar / Completar a Compra (o que faltou comprar da sugestão) / Mostrar Todos / Itens em Trânsito.
- **Filtros de Movimentação**: itens novos (venda ≤ 90 dias), itens com movimentação > 90 dias, itens sem movimentação.
- **Filtros de Aplicação**: Similares, Herança, Influência de Previsão.
- **Filtros de Status do Produto**: Excesso, Nível Adequado, Baixa Exposição a Ruptura, Elevada Exposição a Ruptura, Ruptura — com regras precisas:
  - *Nível Adequado*: saldo > ponto de pedido e ≤ estoque máximo.
  - *Baixa Exposição a Ruptura*: saldo ≤ ponto de pedido e cobertura ≥ lead time.
  - *Elevada Exposição a Ruptura*: saldo ≤ ponto de pedido e cobertura < lead time.
  - *Ruptura*: saldo = 0.
- **Silenciar Produtos**: suprimir notificação/sugestão de compra por período (1 semana / 1–6 meses / data específica), com motivo obrigatório (descontinuar produto, empresa sem caixa, forçar venda do similar, fornecedor sem matéria-prima, item não relevante no momento, preço impraticável) e escopo (só o grupo ou todas as filiais do grupo).
- **Configuração do Fornecedor**: Previsão de Gatilho (dias), Pedido Mínimo de Compra (R$), Data Limite (nenhum/início do mês/quinzenal/fim do mês/outro), Cobertura de Estoque manual on/off.

### 4.9 Análise por Compradores
- Eficiência do Comprador (%) = combinação de "Qualidade do Estoque" + "Momento de Compra".
- Classificação de cada ato de compra:
  - **Primeira Compra**: item novo, nunca comprado.
  - **Compra com Elevada Prematuridade**: comprar item já em excesso.
  - **Compra em Ponto de Pedido**: momento correto (meta a perseguir).
  - **Compra em Exposição a Ruptura**: comprado após o momento ideal — risco de não chegar a tempo.
  - **Compra em Ruptura**: comprado com estoque zerado — perda financeira real.
  - **Sem Comportamento**: recompra de item parado, que não vendeu.
- Comparativo "Ocorrências do Grupo" vs. "Ocorrências do Comprador" — permite benchmarking interno entre compradores.

### 4.10 Indicadores e Relatórios
**Indicadores**: Status Mensal, No Moving, Status Produto, Perda Venda x Ruptura, Percepção de Compras.

**Relatórios**: Curva ABC, Análise de Vendas, Ruptura Geral, Frequência de Saídas (PQR), Análise de Movimentação de Produtos, Excesso de Estoque, Sugestão de Itens para Inativação, Oportunidade de Vendas, Percepção de Compras, Cobertura de Estoque, Pedidos Pendentes, **Indicador OTIF**, Saving de Compras.

### 4.11 Saneamento
- Inativar produtos sem giro/descontinuados.
- Vincular produtos ao ID do comprador (autogestão por carteira).
- Sanear pedidos em aberto que não darão mais entrada.
- Avaliar gestão por categoria e Padronização Descritiva de Materiais (PDM).

> **Leitura crítica para o DRP Intelligence Engine**: o Systock é forte em *análise, classificação e sugestão por elo isolado* (fornecedor, filial, comprador), mas seu conceito de "Ruptura por DRP" aparece apenas como um rótulo em gráfico — não há, no manual, evidência de um motor de **redistribuição entre filiais** (transferência CD↔loja, loja↔loja) nem de **priorização de rede por criticidade multi-elo**. Esse é exatamente o espaço em que o RBM DRP Intelligence Engine deve se diferenciar: transformar "ruptura por DRP" de um indicador em um **motor de decisão de rede**.

---

## 5. Arquitetura da Solução

```
ERP ─┐
WMS ─┼─► Camada de Integração (ETL/Streaming) ─► Data Layer
YMS ─┘                                              │
                                                     ▼
                                  ┌──────────────────────────────────┐
                                  │        DRP Intelligence Core       │
                                  │  ┌───────────┐  ┌───────────────┐  │
                                  │  │ Forecast  │  │  Optimization │  │
                                  │  │  Engine   │  │    Engine     │  │
                                  │  └───────────┘  └───────────────┘  │
                                  │  ┌───────────┐  ┌───────────────┐  │
                                  │  │ DRP Engine│  │   AI Engine   │  │
                                  │  │ (núcleo)  │  │ (RBM TASK 2.0)│  │
                                  │  └───────────┘  └───────────────┘  │
                                  └──────────────────────────────────┘
                                                     │
                                                     ▼
                                   Control Tower / Dashboards / APIs
                                   (Frontend React/Next.js + FastAPI)
```

- **Frontend**: React / Next.js (reaproveitando padrão do RBM TASK Enterprise).
- **Backend**: FastAPI (Python), com o Motor DRP como serviço isolado (para permitir escalonamento independente em picos de recálculo).
- **Banco de dados**: PostgreSQL (dados transacionais e mestres) + Redis (cache de cálculos de cobertura/gatilho de alta frequência).
- **Processamento em lote/streaming**: fila de eventos (ex.: venda, entrada de NF, atualização de trânsito) que dispara recálculo incremental do motor, em vez de apenas batch noturno.
- **Armazenamento de arquivos**: MinIO (exportações de relatórios, anexos de PDM).
- **Infra**: Docker / Kubernetes, com o DRP Engine em pods dedicados (workload de CPU intensivo para otimização/forecast).

---

## 6. Motor DRP — Especificação Detalhada

### 6.1 Entradas do motor
- Estoque atual por elo (CD, filial) e por SKU.
- Estoque em trânsito (pedidos a fornecedor e transferências internas já emitidas).
- Parâmetros por SKU/elo: estoque de segurança, ponto de pedido, estoque máximo, lead time (fornecedor e transferência interna), lote mínimo/múltiplo de compra.
- Projeção de demanda (saída do Forecast Engine) por elo.
- Classificações (Custo de Aquisição, Criticidade de Resultado, Comprabilidade, Frequência de Saída) — usadas para **priorização**, não só para exibição.
- Restrições de rede: capacidade de transporte, janelas de recebimento, custo de transferência entre elos.

### 6.2 Cálculo — Necessidade Líquida
Para cada elo *i* e SKU *s*, no horizonte de replanejamento:

```
Necessidade Líquida(i,s) = Demanda Projetada(i,s) + Estoque Segurança(i,s)
                            − Estoque Disponível(i,s) − Estoque em Trânsito(i,s)
```

Se `Necessidade Líquida > 0` → gerar sugestão de ressuprimento (interno ou externo).

### 6.3 Classificação de Status (herdada e formalizada do Systock)
| Status | Regra |
|---|---|
| Excesso | Saldo > Estoque Máximo |
| Nível Adequado | Ponto de Pedido < Saldo ≤ Estoque Máximo |
| Baixa Exposição a Ruptura | Saldo ≤ Ponto de Pedido **e** Cobertura ≥ Lead Time |
| Elevada Exposição a Ruptura | Saldo ≤ Ponto de Pedido **e** Cobertura < Lead Time |
| Ruptura | Saldo = 0 |
| **Ruptura por DRP** (rede) | Elo local sem risco isolado, mas o CD supridor projeta incapacidade de atender a necessidade líquida agregada dentro do lead time de transferência |

### 6.4 Decisão: Transferência vs. Compra Externa
1. Verificar se existe excedente em outro elo da mesma rede (CD ou filial doadora) capaz de suprir a necessidade dentro da janela de tempo viável.
2. Se sim → gerar **Ordem de Transferência** (prioriza liberar capital parado em excesso e evita nova compra).
3. Se não → gerar **Sugestão de Compra Externa** ao fornecedor (equivalente à sugestão do Systock, mas agora só emitida depois de esgotada a opção de rede).

### 6.5 Priorização
Fila de execução ordenada por score de criticidade:

```
Score = w1·Criticidade de Resultado + w2·Custo de Aquisição
        + w3·(1 / Cobertura Atual) + w4·Frequência de Saída
```
Pesos (`w1..w4`) configuráveis por vertical de cliente (varejo alimentar, home center, distribuidor).

### 6.6 Geração de Ordens
- Ordem de Transferência: elo origem, elo destino, SKU, quantidade, data de embarque sugerida, data de chegada estimada.
- Ordem de Compra: fornecedor, SKU, quantidade (respeitando lote mínimo/múltiplo), data de solicitação e previsão.
- Ambas auditáveis e rastreáveis (trilha de decisão: por que essa quantidade, que dados de forecast/estoque a geraram).

### 6.7 Monitoramento contínuo
- Recalcular a cada evento relevante (venda, entrada de NF, atualização de status de trânsito) — não apenas em batch diário.
- Alertas de desvio: quando a execução real diverge da ordem sugerida (ex.: transferência atrasada), reabrir o cálculo de necessidade.

---

## 7. Modelos Matemáticos e Estatísticos

- **Forecast**: Holt-Winters, ARIMA, Prophet, XGBoost, LSTM — seleção automática do melhor modelo por SKU conforme perfil de demanda (repetitivo, sazonal, esporádico).
- **Estoque de Segurança**: abordagem estatística clássica (nível de serviço-alvo × desvio padrão da demanda × raiz do lead time) e simulação de Monte Carlo para SKUs de alta variabilidade.
- **Otimização de rede**: Programação Linear / Multiobjetivo para alocação de transferências sob restrição de capacidade de transporte; modelagem por Grafos e Fluxo de Rede para rotas CD↔filial↔filial.
- **Classificação de itens**: Curva ABC/PQR (frequência de saída), coeficiente de variação (previsibilidade).

---

## 8. Modelo de Dados (domínios)

| Domínio | Entidades-chave |
|---|---|
| Cadastro | SKU, Fornecedor, Comprador, Grupo de Compras, Segmento, Departamento, Filial, CD |
| Estoque | Saldo por elo, Estoque em Trânsito, Estoque Bloqueado/Reservado/Avaria |
| Forecast | Séries históricas, Projeções, Ajustes manuais (Influenciar Projeção), Herança/Similares |
| DRP | Necessidade Líquida, Ordem de Transferência, Ordem de Compra, Status de Ruptura (COMPRA/DRP), Fila de Priorização |
| Transporte | Rotas, Lead Time por rota, Capacidade, Janelas de recebimento |
| Analytics | Indicadores (OTIF, Fill Rate, Eficiência do Comprador), Relatórios exportáveis |
| Auditoria | Log de decisões do motor, Motivos de Silenciamento, Ajustes manuais com autor/data |
| Segurança | Perfis de acesso, Permissões por Grupo de Compras/Filial |
| Integrações | Conectores ERP/WMS/YMS/TMS |

---

## 9. APIs e Integrações

- **ERP**: cadastro de itens, custos, entrada de NF.
- **WMS**: saldo físico por CD, status de separação.
- **YMS**: gestão de pátio/docas — relevante para prever confirmação de janela de recebimento das transferências.
- **TMS**: lead time real de transporte, rastreamento de transferências em trânsito.
- **BI**: exportação de indicadores e relatórios (Curva ABC, OTIF, Saving de Compras etc.).
- **Compras/Fiscal/E-commerce**: fechamento do ciclo pedido→recebimento→disponibilização para venda.

---

## 10. Dashboards, Indicadores e Relatórios

### 10.1 Control Tower (visão executiva)
Mapa logístico da rede, ruptura prevista vs. realizada, excesso previsto vs. realizado, OTIF, Fill Rate, KPIs consolidados por vertical/cliente.

### 10.2 Indicadores herdados do benchmark Systock (a formalizar com regra de negócio explícita)
- Status Mensal
- No Moving
- Status Produto
- Perda de Venda x Ruptura
- Percepção de Compras

### 10.3 Relatórios herdados do benchmark Systock
Curva ABC, Análise de Vendas, Ruptura Geral, Frequência de Saídas (PQR), Análise de Movimentação de Produtos, Excesso de Estoque, Sugestão de Itens para Inativação, Oportunidade de Vendas, Percepção de Compras, Cobertura de Estoque, Pedidos Pendentes, Indicador OTIF, Saving de Compras.

### 10.4 Indicador novo (diferencial do DRP Intelligence Engine)
- **Taxa de Resolução por Rede**: % da necessidade líquida total resolvida via transferência interna vs. via compra externa — mede a eficácia do motor DRP em evitar compras desnecessárias.
- **Lead Time Efetivo de Transferência** vs. planejado — feedback loop para recalibrar o motor.

---

## 11. Regras de Governança, Saneamento e Auditoria

- Inativação de SKUs sem giro/descontinuados, com vínculo ao comprador responsável (autogestão por carteira).
- Saneamento de pedidos em aberto sem previsão real de entrada.
- Avaliação periódica da gestão por categoria (adequação de classificação ABC/criticidade).
- Padronização Descritiva de Materiais (PDM) como pré-requisito de qualidade de dado para o motor de forecast.
- Toda decisão automática do motor (transferência, compra, silenciamento) deve manter trilha de auditoria com autor (sistema ou usuário), data e motivo.

---

## 12. Roadmap de Entrega

| Fase | Foco | Entregável-chave |
|---|---|---|
| Fase 1 — Fundação | Modelo de dados, cadastros, integrações ERP/WMS básicas | Domínios de Cadastro e Estoque operantes |
| Fase 2 — Forecast | Motor de projeção de demanda multi-modelo | Projeção por SKU/elo com seleção automática de modelo |
| Fase 3 — Motor DRP core | Necessidade líquida, status de ruptura (COMPRA/DRP), geração de ordens de transferência e compra | MVP do motor DRP com priorização por criticidade |
| Fase 4 — Otimização e IA | Otimização de rede (PL/Multiobjetivo), simulação de cenários, RBM TASK 2.0 (agentes autônomos) | Motor de otimização de transferências + agentes de decisão assistida |
| Fase 5 — Torre de Controle | Dashboards executivos, indicadores completos, relatórios, integrações TMS/YMS/BI | Control Tower completo |

> Total planejado: 28 sprints (conforme documento inicial), divididas conforme as fases acima.

---

## 13. Riscos e Pontos em Aberto

- O documento inicial (`Projeto_DRP_Intelligence_Engine_v1.docx`) ainda está em nível de placeholder nos "Capítulos Técnicos 10 a 40" — precisam ser desenvolvidos individualmente (requisitos funcionais, não funcionais, eventos de mensageria, critérios estatísticos, SLAs) à medida que cada módulo entrar em detalhamento.
- Validar com Renato: qual a granularidade real da rede (quantos CDs, quantas filiais por CD) para dimensionar o motor de otimização.
- Definir se o "Silenciar Produto" e a "Cobertura de Estoque Manual" do Systock serão replicados como *overrides* de negócio no motor DRP (recomendado, pois usuários de campo precisam de escape hatch para exceções).
- Confirmar de quem é a responsabilidade de gerar a ordem de transferência física (DRP Intelligence Engine ou sistema de execução logística externo/TMS).

---

*Documento gerado a partir da consolidação de `Projeto_DRP_Intelligence_Engine_v1.docx` e do manual "Treinamento Jornada Systock" (PDF), como ponto de partida para o detalhamento técnico do motor DRP do RBM TASK Enterprise.*
