from pydantic import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_port: int = 8000

    redis_host: str
    redis_port: int
    redis_db: int = 0
    redis_password: str | None = None

    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
