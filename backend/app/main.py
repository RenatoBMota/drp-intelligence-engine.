from fastapi import FastAPI

from app.api.routes import analytics, drp, estoque, filiais, forecast, fornecedores, health, otimizacao, skus
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health.router)
app.include_router(skus.router)
app.include_router(fornecedores.router)
app.include_router(filiais.router)
app.include_router(forecast.router)
app.include_router(drp.router)
app.include_router(estoque.router)
app.include_router(analytics.router)
app.include_router(otimizacao.router)
