from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    APP_ENV: str = "local"
    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    CORS_ORIGINS: str = "http://localhost:3000"
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = ""  # Model name (defaults to provider-specific: gpt-4o-mini for OpenAI, gemini-2.0-flash-exp for Gemini)

settings = Settings()