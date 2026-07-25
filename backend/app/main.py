from fastapi import FastAPI

from app.api.routes import filiais, fornecedores, health, skus
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health.router)
app.include_router(skus.router)
app.include_router(fornecedores.router)
app.include_router(filiais.router)
