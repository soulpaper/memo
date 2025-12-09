from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "KIS Stock Portfolio"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/kis_portfolio"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # KIS API Settings (Default/Global if needed, but mostly per user)
    # But we might need a general app key for some public data if applicable, 
    # though KIS usually requires per-account auth for trading.
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
