from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DRP Intelligence Engine"
    environment: str = "development"

    database_url: str = "postgresql+asyncpg://drp:drp@localhost:5432/drp"
    redis_url: str = "redis://localhost:6379/0"

    # ERP/WMS legado do cliente (roadmap seção 13, issue #11): WinThor (TOTVS).
    # None por padrão — sem isso configurado, os conectores WinThor não são
    # instanciados e o app usa os Null*Connector (nenhuma conexão é tentada).
    # Dialeto depende da instalação do cliente: "oracle+oracledb://user:pass@host:port/?service_name=..."
    # (Oracle, a maioria das instalações) ou "mssql+pyodbc://..." (SQL Server).
    winthor_database_url: str | None = None


settings = Settings()
