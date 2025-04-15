from pydantic_settings import BaseSettings  # считываем значения из .env


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    REDIS_URL: str = "redis://localhost:6379/0"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"  # откуда берем переменные
        extra = "ignore"  # игнорируем лишние переменные в .env


settings = Settings()
