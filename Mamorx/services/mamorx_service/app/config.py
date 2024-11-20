from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MAMORX API Service"
    version: str = "0.1.0"
    redis_host: str = "redis"
    redis_port: str = "6379"
    redis_queue_name: str = "review-queue"

settings = Settings()