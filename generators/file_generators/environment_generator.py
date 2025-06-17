"""
Environment Generator
Generates database-specific .env files
"""

from ..base_generator import BaseGenerator
from ..config import DatabaseType, AuthType


class EnvironmentGenerator(BaseGenerator):
    """Generates environment configuration files"""

    def generate(self):
        """Generate .env file"""
        env_content = self._get_env_template()
        self.write_file(f"{self.config.path}/.env", env_content)

        # Also generate .env.example
        env_example_content = self._get_env_example_template()
        self.write_file(f"{self.config.path}/.env.example", env_example_content)

    def _get_env_template(self) -> str:
        """Get environment template with actual values"""
        template = f"""# Application Configuration
APP_NAME={self.config.name}
APP_VERSION=1.0.0
DEBUG=true
API_PREFIX=/api/v1

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database Configuration
{self._get_database_env_vars()}

# Security Configuration
{self._get_security_env_vars()}

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=

{self._get_additional_env_vars()}
"""
        return template

    def _get_env_example_template(self) -> str:
        """Get environment example template with placeholder values"""
        template = f"""# Application Configuration
APP_NAME=your-app-name
APP_VERSION=1.0.0
DEBUG=true
API_PREFIX=/api/v1

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database Configuration
{self._get_database_env_vars_example()}

# Security Configuration
{self._get_security_env_vars_example()}

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=

{self._get_additional_env_vars_example()}
"""
        return template

    def _get_database_env_vars(self) -> str:
        """Get database-specific environment variables"""
        if self.config.database_type == DatabaseType.SQLITE:
            return "DATABASE_URL=sqlite:///./app.db"
        elif self.config.database_type == DatabaseType.POSTGRESQL:
            return """DATABASE_URL=postgresql://postgres:password@localhost:5432/fastapi_db
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=fastapi_db"""
        elif self.config.database_type == DatabaseType.MYSQL:
            return """DATABASE_URL=mysql://root:password@localhost:3306/fastapi_db
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=fastapi_db"""
        elif self.config.database_type == DatabaseType.MONGODB:
            return """MONGODB_URL=mongodb://localhost:27017/fastapi_db
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB_NAME=fastapi_db
MONGODB_USERNAME=
MONGODB_PASSWORD="""
        elif self.config.database_type == DatabaseType.REDIS:
            return """REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD="""

        return "DATABASE_URL=sqlite:///./app.db"

    def _get_database_env_vars_example(self) -> str:
        """Get database-specific environment variables with example values"""
        if self.config.database_type == DatabaseType.SQLITE:
            return "DATABASE_URL=sqlite:///./app.db"
        elif self.config.database_type == DatabaseType.POSTGRESQL:
            return """DATABASE_URL=postgresql://username:password@localhost:5432/dbname
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database"""
        elif self.config.database_type == DatabaseType.MYSQL:
            return """DATABASE_URL=mysql://username:password@localhost:3306/dbname
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database"""
        elif self.config.database_type == DatabaseType.MONGODB:
            return """MONGODB_URL=mongodb://localhost:27017/dbname
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB_NAME=your_database
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password"""
        elif self.config.database_type == DatabaseType.REDIS:
            return """REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password"""

        return "DATABASE_URL=sqlite:///./app.db"

    def _get_security_env_vars(self) -> str:
        """Get security-related environment variables"""
        if self.config.auth_type == AuthType.NONE:
            return "# No authentication configured"

        vars_list = [
            "SECRET_KEY=your-secret-key-change-this-in-production-make-it-long-and-random",
            "ACCESS_TOKEN_EXPIRE_MINUTES=30",
            "ALGORITHM=HS256",
        ]

        if self.config.auth_type == AuthType.OAUTH2:
            vars_list.extend(
                [
                    "OAUTH2_CLIENT_ID=your-oauth2-client-id",
                    "OAUTH2_CLIENT_SECRET=your-oauth2-client-secret",
                    "OAUTH2_REDIRECT_URI=http://localhost:8000/auth/callback",
                ]
            )
        elif self.config.auth_type == AuthType.API_KEY:
            vars_list.append("API_KEY_HEADER=X-API-Key")

        return "\n".join(vars_list)

    def _get_security_env_vars_example(self) -> str:
        """Get security-related environment variables with example values"""
        if self.config.auth_type == AuthType.NONE:
            return "# No authentication configured"

        vars_list = [
            "SECRET_KEY=change-this-to-a-secure-random-string",
            "ACCESS_TOKEN_EXPIRE_MINUTES=30",
            "ALGORITHM=HS256",
        ]

        if self.config.auth_type == AuthType.OAUTH2:
            vars_list.extend(
                [
                    "OAUTH2_CLIENT_ID=your-oauth2-client-id",
                    "OAUTH2_CLIENT_SECRET=your-oauth2-client-secret",
                    "OAUTH2_REDIRECT_URI=http://localhost:8000/auth/callback",
                ]
            )
        elif self.config.auth_type == AuthType.API_KEY:
            vars_list.append("API_KEY_HEADER=X-API-Key")

        return "\n".join(vars_list)

    def _get_additional_env_vars(self) -> str:
        """Get additional environment variables based on configuration"""
        vars_list = []

        if self.config.include_monitoring:
            vars_list.extend(
                [
                    "# Monitoring Configuration",
                    "ENABLE_METRICS=true",
                    "METRICS_PORT=9090",
                ]
            )

        if self.config.include_celery:
            vars_list.extend(
                [
                    "# Celery Configuration",
                    "CELERY_BROKER_URL=redis://localhost:6379/0",
                    "CELERY_RESULT_BACKEND=redis://localhost:6379/0",
                    "CELERY_TASK_SERIALIZER=json",
                    "CELERY_RESULT_SERIALIZER=json",
                    "CELERY_ACCEPT_CONTENT=json",
                    "CELERY_TIMEZONE=UTC",
                    "CELERY_ENABLE_UTC=true",
                ]
            )

        return "\n".join(vars_list) if vars_list else ""

    def _get_additional_env_vars_example(self) -> str:
        """Get additional environment variables examples"""
        vars_list = []

        if self.config.include_monitoring:
            vars_list.extend(
                [
                    "# Monitoring Configuration",
                    "ENABLE_METRICS=true",
                    "METRICS_PORT=9090",
                ]
            )

        if self.config.include_celery:
            vars_list.extend(
                [
                    "# Celery Configuration",
                    "CELERY_BROKER_URL=redis://localhost:6379/0",
                    "CELERY_RESULT_BACKEND=redis://localhost:6379/0",
                    "CELERY_TASK_SERIALIZER=json",
                    "CELERY_RESULT_SERIALIZER=json",
                    "CELERY_ACCEPT_CONTENT=json",
                    "CELERY_TIMEZONE=UTC",
                    "CELERY_ENABLE_UTC=true",
                ]
            )

        return "\n".join(vars_list) if vars_list else ""
