from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analytics, drp, estoque, filiais, forecast, fornecedores, health, otimizacao, skus
from app.core.config import settings

app = FastAPI(title=settings.app_name)

# Wildcard de origem só é seguro aqui porque não há cookies/credenciais
# envolvidas (nenhuma autenticação foi implementada ainda). Restringir a
# origens específicas quando a autenticação existir.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(skus.router)
app.include_router(fornecedores.router)
app.include_router(filiais.router)
app.include_router(forecast.router)
app.include_router(drp.router)
app.include_router(estoque.router)
app.include_router(analytics.router)
app.include_router(otimizacao.router)
