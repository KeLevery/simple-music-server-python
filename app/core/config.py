from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 9080
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # MySQL Database
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "vibe_music"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 1800

    # Redis (DB 1 as per Spring Boot config)
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = "root"
    REDIS_DB: int = 1

    # MinIO
    MINIO_ENDPOINT: str = "127.0.0.1:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "vibe-music-data"
    MINIO_PUBLIC_URL: str = "http://localhost:9000"

    # JWT & Auth
    JWT_SECRET_KEY: str = "SIMPLE_MUSIC"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    REDIS_TOKEN_EXPIRE_SECONDS: int = 21600

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """SQLAlchemy Async MySQL URL using asyncmy driver"""
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

settings = Settings()
