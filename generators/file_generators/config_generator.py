"""
Config Generator
Generates configuration management files
"""

from ..base_generator import BaseGenerator
from ..config import DatabaseType


class ConfigGenerator(BaseGenerator):
    """Generates configuration files"""

    def generate(self):
        """Generate config.py file"""
        content = self._get_config_template()
        self.write_file(f"{self.config.path}/app/core/config.py", content)

    def _get_config_template(self) -> str:
        """Get the configuration template"""
        template = '''"""
Configuration Settings
Centralized configuration management using Pydantic Settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "{project_name}"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "{database_url}"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    {additional_settings}
    
    @field_validator("ALLOWED_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
'''

        # Customize based on database type
        database_url = self._get_database_url()
        additional_settings = self._get_additional_settings()

        return self.format_template(
            template.format(
                database_url=database_url, additional_settings=additional_settings, project_name=self.get_template_vars()['project_name']
            )
        )

    def _get_database_url(self) -> str:
        """Get default database URL based on type"""
        if self.config.database_type == DatabaseType.SQLITE:
            return "sqlite:///./app.db"
        elif self.config.database_type == DatabaseType.POSTGRESQL:
            return "postgresql://user:password@localhost/dbname"
        elif self.config.database_type == DatabaseType.MYSQL:
            return "mysql://user:password@localhost/dbname"
        elif self.config.database_type == DatabaseType.MONGODB:
            return "mongodb://localhost:27017/dbname"
        elif self.config.database_type == DatabaseType.REDIS:
            return "redis://localhost:6379/0"
        return "sqlite:///./app.db"

    def _get_additional_settings(self) -> str:
        """Get additional settings based on configuration"""
        settings = []

        if self.config.include_monitoring:
            settings.append(
                """
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090"""
            )

        if self.config.include_celery:
            settings.append(
                """
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True"""
            )

        if self.config.database_type == DatabaseType.REDIS:
            settings.append(
                """
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None"""
            )

        return "".join(settings)
