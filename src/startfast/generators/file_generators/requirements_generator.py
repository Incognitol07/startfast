"""
Requirements Generator
Generates requirements.txt with appropriate dependencies
"""

from ...generators.base_generator import BaseGenerator
from ...core.config import DatabaseType, AuthType


class RequirementsGenerator(BaseGenerator):
    """Generates requirements.txt file"""

    def generate(self):
        """Generate requirements.txt"""
        requirements = self._get_base_requirements()
        requirements.extend(self._get_database_requirements())
        requirements.extend(self._get_auth_requirements())
        requirements.extend(self._get_optional_requirements())

        content = "# FastAPI Dependencies\n"
        content += "\n".join(sorted(requirements))
        content += "\n"

        self.write_file(f"{self.config.path}/requirements.txt", content)

    def _get_base_requirements(self) -> list:
        """Get base FastAPI requirements"""
        requirements = [
            "fastapi>=0.104.1",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.5.0",
            "pydantic-settings>=2.1.0",
            "python-multipart>=0.0.6",
        ]

        if self.config.is_async:
            requirements.extend(
                [
                    "aiofiles>=23.2.1",
                    "httpx>=0.25.2",
                ]
            )
        else:
            requirements.append("requests>=2.31.0")

        return requirements

    def _get_database_requirements(self) -> list:
        """Get database-specific requirements"""
        requirements = []

        if self.config.database_type == DatabaseType.SQLITE:
            requirements.extend(
                [
                    "sqlalchemy>=2.0.23",
                    "aiosqlite>=0.19.0" if self.config.is_async else "sqlite3",
                ]
            )
        elif self.config.database_type == DatabaseType.POSTGRESQL:
            requirements.extend(
                [
                    "sqlalchemy>=2.0.23",
                    (
                        "asyncpg>=0.29.0"
                        if self.config.is_async
                        else "psycopg2-binary>=2.9.9"
                    ),
                ]
            )
        elif self.config.database_type == DatabaseType.MYSQL:
            requirements.extend(
                [
                    "sqlalchemy>=2.0.23",
                    "aiomysql>=0.2.0" if self.config.is_async else "PyMySQL>=1.1.0",
                ]
            )
        elif self.config.database_type == DatabaseType.MONGODB:
            requirements.extend(
                [
                    "motor>=3.3.2" if self.config.is_async else "pymongo>=4.6.0",
                    "beanie>=1.23.6" if self.config.is_async else "mongoengine>=0.27.0",
                ]
            )
        elif self.config.database_type == DatabaseType.REDIS:
            requirements.extend(
                [
                    "redis>=5.0.1",
                    "aioredis>=2.0.1" if self.config.is_async else "",
                ]
            )

        return [req for req in requirements if req]  # Filter empty strings

    def _get_auth_requirements(self) -> list:
        """Get authentication-specific requirements"""
        requirements = []

        if self.config.auth_type in [AuthType.JWT, AuthType.OAUTH2]:
            requirements.extend(
                [
                    "python-jose[cryptography]>=3.3.0",
                    "passlib[bcrypt]>=1.7.4",
                    "python-multipart>=0.0.6",
                ]
            )

        if self.config.auth_type == AuthType.OAUTH2:
            requirements.append("python-oauth2>=1.1.1")

        return requirements

    def _get_optional_requirements(self) -> list:
        """Get optional requirements based on configuration"""
        requirements = []

        if self.config.include_tests:
            requirements.extend(
                [
                    "pytest>=7.4.3",
                    "pytest-asyncio>=0.21.1",
                    "httpx>=0.25.2",
                    "pytest-cov>=4.1.0",
                ]
            )

        if self.config.include_monitoring:
            requirements.extend(
                [
                    "prometheus-client>=0.19.0",
                    "structlog>=23.2.0",
                ]
            )

        if self.config.include_celery:
            requirements.extend(
                [
                    "celery>=5.3.4",
                    "redis>=5.0.1",
                ]
            )

        if self.config.is_advanced:
            requirements.extend(
                [
                    "alembic>=1.13.1",  # Database migrations
                    "python-dotenv>=1.0.0",  # Environment variables
                    "rich>=13.7.0",  # Rich console output
                    "typer>=0.9.0",  # CLI interface
                ]
            )

        return requirements
