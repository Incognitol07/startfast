"""
Docker Generator
Generates Docker configuration files
"""

from ..base_generator import BaseGenerator
from ..config import DatabaseType


class DockerGenerator(BaseGenerator):
    """Generates Docker configuration files"""

    def should_generate(self) -> bool:
        """Only generate if Docker is enabled"""
        return self.config.include_docker

    def generate(self):
        """Generate Docker files"""
        # Generate Dockerfile
        dockerfile_content = self._get_dockerfile_template()
        self.write_file(f"{self.config.path}/Dockerfile", dockerfile_content)

        # Generate docker-compose.yml
        compose_content = self._get_compose_template()
        self.write_file(f"{self.config.path}/docker-compose.yml", compose_content)

        # Generate .dockerignore
        dockerignore_content = self._get_dockerignore_template()
        self.write_file(f"{self.config.path}/.dockerignore", dockerignore_content)

    def _get_dockerfile_template(self) -> str:
        """Get Dockerfile template"""
        template = """# Use Python {python_version} slim image
FROM python:{python_version}-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        build-essential \\
        curl \\
        && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \\
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \\
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

        return self.format_template(template)

    def _get_compose_template(self) -> str:
        """Get docker-compose.yml template"""
        template = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DATABASE_URL={database_url}
      - SECRET_KEY=your-secret-key-change-in-production
    volumes:
      - ./app:/app/app
    depends_on:
{database_service}
    restart: unless-stopped
    networks:
      - {project_name_snake}_network

{database_service_definition}

{additional_services}

networks:
  {project_name_snake}_network:
    driver: bridge

volumes:
{volumes}
"""

        # Customize based on database type
        database_url, database_service, database_service_definition, volumes = (
            self._get_database_config()
        )
        additional_services = (
            self._get_additional_services()
        )  # Create snake_case version of project name
        project_name_snake = (
            self.config.name.lower().replace("-", "_").replace(" ", "_")
        )

        return self.format_template(
            template.format(
                project_name_snake=project_name_snake,
                database_url=database_url,
                database_service=database_service,
                database_service_definition=database_service_definition,
                additional_services=additional_services,
                volumes=volumes,
            )
        )

    def _get_database_config(self) -> tuple:
        """Get database configuration for docker-compose"""
        if self.config.database_type == DatabaseType.POSTGRESQL:
            database_url = (
                "postgresql://postgres:password@postgres:5432/{project_name_snake}"
            )
            database_service = "      - postgres"
            database_service_definition = """  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB={project_name_snake}
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - {project_name_snake}_network"""
            volumes = "  postgres_data:"

        elif self.config.database_type == DatabaseType.MYSQL:
            database_url = "mysql://root:password@mysql:3306/{project_name_snake}"
            database_service = "      - mysql"
            database_service_definition = """  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE={project_name_snake}
      - MYSQL_ROOT_PASSWORD=password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    networks:
      - {project_name_snake}_network"""
            volumes = "  mysql_data:"

        elif self.config.database_type == DatabaseType.MONGODB:
            database_url = "mongodb://mongo:27017/{project_name_snake}"
            database_service = "      - mongo"
            database_service_definition = """  mongo:
    image: mongo:7.0
    environment:
      - MONGO_INITDB_DATABASE={project_name_snake}
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
    networks:
      - {project_name_snake}_network"""
            volumes = "  mongo_data:"

        elif self.config.database_type == DatabaseType.REDIS:
            database_url = "redis://redis:6379/0"
            database_service = "      - redis"
            database_service_definition = """  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - {project_name_snake}_network"""
            volumes = "  redis_data:"

        else:  # SQLite
            database_url = "sqlite:///./app.db"
            database_service = ""
            database_service_definition = ""
            volumes = ""

        return database_url, database_service, database_service_definition, volumes

    def _get_additional_services(self) -> str:
        """Get additional services for docker-compose"""
        services = []

        if self.config.include_celery:
            services.append(
                """  celery_worker:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL={database_url}
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis
    volumes:
      - ./app:/app/app
    networks:
      - {project_name_snake}_network

  celery_beat:
    build: .
    command: celery -A app.tasks.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL={database_url}
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis
    volumes:
      - ./app:/app/app
    networks:
      - {project_name_snake}_network"""
            )

        if self.config.include_monitoring:
            services.append(
                """  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - {project_name_snake}_network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - {project_name_snake}_network"""
            )

        return "\\n\\n".join(services)

    def _get_dockerignore_template(self) -> str:
        """Get .dockerignore template"""
        return """# Git
.git
.gitignore

# Docker
Dockerfile
docker-compose.yml
.dockerignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Documentation
docs/_build/

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Environment variables
.env
.env.local
.env.*.local

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Node.js (if using frontend)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build artifacts
build/
dist/
*.egg-info/
"""
