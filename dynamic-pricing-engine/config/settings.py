"""Centralized application configuration."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"

    # Kafka
    KAFKA_BROKER: str = os.getenv("KAFKA_BROKER", "kafka:9092")
    KAFKA_SCRAPER_TOPIC: str = os.getenv("KAFKA_SCRAPER_TOPIC", "raw_prices")
    KAFKA_PRICES_TOPIC: str = os.getenv("KAFKA_PRICES_TOPIC", "recommended_prices")
    KAFKA_DLQ_TOPIC: str = os.getenv("KAFKA_DLQ_TOPIC", "dead_letter_queue")

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "3600"))

    # PostgreSQL
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "pricing_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "pricing_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "pricing_db")

    # API Services
    SCRAPER_HOST: str = os.getenv("SCRAPER_HOST", "0.0.0.0")
    SCRAPER_PORT: int = int(os.getenv("SCRAPER_PORT", "8001"))
    PRICING_API_HOST: str = os.getenv("PRICING_API_HOST", "0.0.0.0")
    PRICING_API_PORT: int = int(os.getenv("PRICING_API_PORT", "8000"))

    # Pricing Rules
    MINIMUM_MARGIN: float = float(os.getenv("MINIMUM_MARGIN", "0.10"))
    MAXIMUM_MARGIN: float = float(os.getenv("MAXIMUM_MARGIN", "0.50"))
    ELASTICITY_FACTOR: float = float(os.getenv("ELASTICITY_FACTOR", "1.5"))

    # Performance
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "1000"))
    WORKER_THREADS: int = int(os.getenv("WORKER_THREADS", "4"))

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"


settings = Settings()
