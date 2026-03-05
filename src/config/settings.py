"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic (Claude)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    anthropic_temperature: float = 0.3

    # Redis
    redis_url: str = "redis://localhost:6379/1"

    # Evolution API (WhatsApp)
    evolution_api_url: str = "http://localhost:8080"
    evolution_api_key: str = ""
    evolution_instance: str = "pitcore-whatsapp"

    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "production"
    log_level: str = "info"

    # CORS
    cors_origins: str = "https://pitcore.online,http://localhost:3000"

    # Conversation
    conversation_ttl_hours: int = 24

    # Escalation
    escalation_whatsapp: str = ""
    escalation_notify_email: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
