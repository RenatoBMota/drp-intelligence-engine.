# DRP Intelligence Engine

Plataforma de planejamento de distribuição (DRP), otimização de estoques,
forecast e inteligência artificial para redes com múltiplos CDs e filiais.
Ver `DRP_INTELLIGENCE_ENGINE_ROADMAP.md` para a visão completa, benchmark
funcional (Systock), arquitetura e roadmap de entrega em 5 fases.

Gestão do projeto (Issues, Epics, Milestones, Project Board) está em
[GitHub Issues](../../issues) — 5 Epics (um por fase) com sub-issues
detalhadas. Rode `scripts/github_bootstrap.sh` (requer `gh` CLI autenticado)
para criar as Milestones, Labels e o Project Board correspondentes.

## Status

**Fase 1 — Fundação**: em andamento. Domínios de Cadastro, Estoque,
Auditoria e Segurança modelados e operantes via API.

## Stack

- **Backend**: FastAPI + SQLAlchemy (async) + Alembic + PostgreSQL + Redis
- **Frontend**: Next.js (App Router) + TypeScript + Tailwind CSS
- **Infra local**: Docker Compose

## Rodando localmente

```bash
cp .env.example .env
docker compose up --build
```

- Backend: http://localhost:8000 (docs em `/docs`)
- Frontend: http://localhost:3000

A migration inicial roda automaticamente ao subir o container `backend`
(`alembic upgrade head`).

### Sem Docker

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (em outro terminal)
cd frontend
npm install
npm run dev
```

## Estrutura

```
backend/
  app/
    models/       # SQLAlchemy — domínios Cadastro, Estoque, Auditoria, Segurança
    schemas/       # Pydantic
    api/routes/    # Endpoints REST
    connectors/    # Interfaces de integração ERP/WMS (stubs — sistema alvo em aberto)
  alembic/         # Migrations
frontend/
  app/             # Next.js App Router
```
