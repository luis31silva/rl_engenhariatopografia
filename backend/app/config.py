"""Configuração da aplicação, lida a partir de variáveis de ambiente."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Aplicação
    app_name: str = "RL Eng & Top - Gestão"
    environment: str = "development"

    # Base de dados. Se DATABASE_URL não for definido, usa SQLite (útil para dev/testes).
    # Em produção (Aiven/MySQL), definir DATABASE_URL, por exemplo:
    #   mysql+pymysql://user:password@host:port/dbname
    database_url: str = "sqlite:///./dev.db"

    # SSL na ligação MySQL. O Aiven exige TLS; manter True em produção.
    # (Ignorado quando a BD é SQLite.)
    db_ssl: bool = True

    # Autenticação (JWT).
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 60 * 24

    # Credenciais do utilizador inicial (usadas pelo script de seed).
    initial_username: str = "admin"
    initial_password: str = "admin"

    # Dados do gabinete (usados nas faturas/recibos em PDF).
    empresa_nome: str = "RL - Engenharia & Topografia"
    empresa_morada: str = ""
    empresa_nif: str = ""
    empresa_contacto: str = ""

    # CORS — lista de origens permitidas separadas por vírgula.
    # Ex.: "http://localhost:5173,https://a-minha-app.onrender.com"
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
