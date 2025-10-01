"""
애플리케이션 설정
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 애플리케이션 설정
    APP_NAME: str = "ETFolio"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # 데이터베이스 설정 (PostgreSQL 우선, 로컬에서는 SQLite)
    DATABASE_URL: str = "sqlite:///./etfolio.db"
    POSTGRES_URL: Optional[str] = None  # Vercel이 자동 설정
    POSTGRES_POSTGRES_URL: Optional[str] = None  # Neon Custom Prefix 중복 대응
    
    @property
    def db_url(self) -> str:
        """PostgreSQL이 있으면 우선 사용, 없으면 SQLite"""
        # POSTGRES_URL 또는 POSTGRES_POSTGRES_URL 둘 다 지원
        return self.POSTGRES_URL or self.POSTGRES_POSTGRES_URL or self.DATABASE_URL
    
    # CORS 설정
    CORS_ORIGINS: list = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # API 설정
    API_V1_STR: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

