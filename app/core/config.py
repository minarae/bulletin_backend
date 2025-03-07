from typing import Any, Dict, Optional
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""

    PROJECT_NAME: str = "Bulletin Backend"
    API_V1_STR: str = "/api/v1"

    # JWT 설정
    SECRET_KEY: str = "your-secret-key-for-jwt"  # 실제 운영 환경에서는 환경 변수로 관리
    REFRESH_SECRET_KEY: str = "your-refresh-secret-key-for-jwt"  # 실제 운영 환경에서는 환경 변수로 관리
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8  # 액세스 토큰 만료 시간 (8시간)
    REFRESH_TOKEN_EXPIRE_HOURS: int = 24  # 리프레시 토큰 만료 시간 (24시간)

    DEBUG: bool = False

    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=int(values.data.get("POSTGRES_PORT")),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )


settings = Settings()
