import os
import logging
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
                app_name: str = "Gestronomy"
                app_env: str = "production"
                debug: bool = True
                backend_url: str = "http://localhost:8000"
                frontend_url: str = "http://localhost:3000"
                cors_origins: str = "http://localhost:3000"
                database_url: str = "postgresql+asyncpg://gestronomy:gestronomy@localhost:5432/gestronomy"
                database_url_sync: str = "postgresql://gestronomy:gestronomy@localhost:5432/gestronomy"
                redis_url: str = "redis://localhost:6379/0"
                secret_key: str = "change-me"
                access_token_expire_minutes: int = 30
                refresh_token_expire_days: int = 7
                algorithm: str = "HS256"
                max_request_size_bytes: int = 1048576
                auth_rate_limit_per_minute: int = 12
                public_rate_limit_per_minute: int = 60
                stripe_api_key: str = ""
                stripe_webhook_secret: str = ""
                anthropic_api_key: str = ""
                resend_api_key: str = ""
                voicebooker_secret: str = "dev_secret_key"
                model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

settings = Settings()
