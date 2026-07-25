#!/usr/bin/env bash
# Bootstrap script: cria Milestones, Labels e um Project (v2) board para
# renatobmota/drp-intelligence-engine., e vincula as issues já criadas.
#
# Pré-requisitos: `gh` CLI instalado e autenticado (`gh auth login`) com um
# usuário que tenha acesso de escrita/admin ao repositório. Rode a partir de
# qualquer diretório.
#
# As issues e a hierarquia Epic -> sub-issues já foram criadas via API pelo
# Claude Code. Este script cobre apenas o que a API/MCP disponível não
# conseguiu criar diretamente: Milestones, Labels custom e o Project Board.
set -euo pipefail

REPO="renatobmota/drp-intelligence-engine."
OWNER="renatobmota"

echo "==> Criando labels"
declare -A LABELS=(
  ["epic"]="6f42c1:Épico — agrupa as stories de uma fase"
  ["fase-1"]="0e8a16:Fase 1 — Fundação"
  ["fase-2"]="0e8a16:Fase 2 — Forecast"
  ["fase-3"]="0e8a16:Fase 3 — Motor DRP Core"
  ["fase-4"]="0e8a16:Fase 4 — Otimização e IA"
  ["fase-5"]="0e8a16:Fase 5 — Torre de Controle"
  ["area:cadastro"]="1d76db:Domínio de Cadastro/Estoque"
  ["area:forecast"]="1d76db:Domínio de Forecast"
  ["area:drp-engine"]="1d76db:Motor DRP"
  ["area:otimizacao"]="1d76db:Otimização/IA"
  ["area:control-tower"]="1d76db:Torre de Controle"
  ["decisao-em-aberto"]="d93f0b:Ponto de decisão/risco do roadmap (seção 13)"
)
for name in "${!LABELS[@]}"; do
  color="${LABELS[$name]%%:*}"
  desc="${LABELS[$name]#*:}"
  gh label create "$name" --repo "$REPO" --color "$color" --description "$desc" --force
done

echo "==> Criando milestones (uma por fase)"
declare -A MILESTONES=(
  ["Fase 1 — Fundação"]="Modelo de dados, cadastros, integrações ERP/WMS básicas"
  ["Fase 2 — Forecast"]="Motor de projeção de demanda multi-modelo"
  ["Fase 3 — Motor DRP Core (MVP)"]="Necessidade líquida, status de ruptura, geração de ordens"
  ["Fase 4 — Otimização e IA"]="Otimização de rede + agentes de decisão assistida"
  ["Fase 5 — Torre de Controle"]="Dashboards executivos, indicadores, relatórios, integrações TMS/YMS/BI"
)
for title in "${!MILESTONES[@]}"; do
  gh api "repos/$REPO/milestones" -f title="$title" -f description="${MILESTONES[$title]}" --silent || true
done

echo "==> Atribuindo milestones e labels de fase às issues, por prefixo do título"
declare -A PHASE_MAP=(
  ["[Fase 1]"]="Fase 1 — Fundação"
  ["[Epic] Fase 1"]="Fase 1 — Fundação"
  ["[Fase 2]"]="Fase 2 — Forecast"
  ["[Epic] Fase 2"]="Fase 2 — Forecast"
  ["[Fase 3]"]="Fase 3 — Motor DRP Core (MVP)"
  ["[Epic] Fase 3"]="Fase 3 — Motor DRP Core (MVP)"
  ["[Fase 4]"]="Fase 4 — Otimização e IA"
  ["[Epic] Fase 4"]="Fase 4 — Otimização e IA"
  ["[Fase 5]"]="Fase 5 — Torre de Controle"
  ["[Epic] Fase 5"]="Fase 5 — Torre de Controle"
)

for prefix in "${!PHASE_MAP[@]}"; do
  milestone="${PHASE_MAP[$prefix]}"
  gh issue list --repo "$REPO" --search "\"$prefix\" in:title" --state all --json number --jq '.[].number' | while read -r num; do
    gh issue edit "$num" --repo "$REPO" --milestone "$milestone"
  done
done

echo "==> Aplicando labels epic/fase-N"
gh issue list --repo "$REPO" --search '"[Epic]" in:title' --state all --json number --jq '.[].number' | while read -r num; do
  gh issue edit "$num" --repo "$REPO" --add-label epic
done
for i in 1 2 3 4 5; do
  gh issue list --repo "$REPO" --search "\"[Fase $i]\" in:title" --state all --json number --jq '.[].number' | while read -r num; do
    gh issue edit "$num" --repo "$REPO" --add-label "fase-$i"
  done
  gh issue list --repo "$REPO" --search "\"[Epic] Fase $i\" in:title" --state all --json number --jq '.[].number' | while read -r num; do
    gh issue edit "$num" --repo "$REPO" --add-label "fase-$i"
  done
done

echo "==> Aplicando label decisao-em-aberto"
gh issue list --repo "$REPO" --search '"[Decisão]" in:title' --state all --json number --jq '.[].number' | while read -r num; do
  gh issue edit "$num" --repo "$REPO" --add-label decisao-em-aberto
done

echo "==> Criando Project (v2) board"
PROJECT_NUM=$(gh project create --owner "$OWNER" --title "DRP Intelligence Engine — Roadmap" --format json --jq '.number')
echo "Project number: $PROJECT_NUM"

gh project field-create "$PROJECT_NUM" --owner "$OWNER" --name "Fase" --data-type SINGLE_SELECT \
  --single-select-options "Fase 1,Fase 2,Fase 3,Fase 4,Fase 5"

echo "==> Adicionando todas as issues ao board"
gh issue list --repo "$REPO" --state all --json url --jq '.[].url' | while read -r url; do
  gh project item-add "$PROJECT_NUM" --owner "$OWNER" --url "$url"
done

echo "==> Concluído. Abra o board com: gh project view $PROJECT_NUM --owner $OWNER --web"
