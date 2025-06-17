"""
Documentation Generator
Generates documentation files and configuration
"""

from ..base_generator import BaseGenerator
from ..config import ProjectType, AuthType


class DocsGenerator(BaseGenerator):
    """Generates documentation files"""

    def should_generate(self) -> bool:
        """Only generate if docs are enabled"""
        return self.config.include_docs

    def generate(self):
        """Generate documentation files"""
        # Generate API documentation
        api_docs_content = self._get_api_docs_template()
        self.write_file(f"{self.config.path}/docs/api.md", api_docs_content)

        # Generate deployment guide
        deployment_docs_content = self._get_deployment_docs_template()
        self.write_file(
            f"{self.config.path}/docs/deployment.md", deployment_docs_content
        )

        # Generate development guide
        development_docs_content = self._get_development_docs_template()
        self.write_file(
            f"{self.config.path}/docs/development.md", development_docs_content
        )

        # Generate configuration docs
        config_docs_content = self._get_config_docs_template()
        self.write_file(
            f"{self.config.path}/docs/configuration.md", config_docs_content
        )

        # Generate contributing guide
        contributing_content = self._get_contributing_template()
        self.write_file(f"{self.config.path}/CONTRIBUTING.md", contributing_content)

    def _get_api_docs_template(self) -> str:
        """Get API documentation template"""
        template = """# {project_name_pascal} API Documentation

## Overview

This document provides detailed information about the {project_name_pascal} API endpoints, request/response formats, and authentication.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

{auth_section}

## Common Response Formats

### Success Response
```json
{{
    "message": "Operation completed successfully",
    "data": {{}}
}}
```

### Error Response
```json
{{
    "error": "Error type",
    "message": "Detailed error message",
    "details": {{}}
}}
```

## Endpoints

### Health Check

#### GET /health
Check the health status of the API.

**Response:**
```json
{{
    "status": "healthy",
    "service": "{project_name}",
    "timestamp": "2024-01-01T12:00:00Z"
}}
```

{crud_endpoints}

{project_specific_endpoints}

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content returned
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Rate Limiting

The API implements rate limiting to ensure fair usage:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

When rate limit is exceeded, the API returns a `429 Too Many Requests` status code.

## Pagination

For endpoints that return lists, pagination is supported:

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 10, max: 100)
- `sort_by` (string): Field to sort by
- `sort_order` (string): Sort order ('asc' or 'desc')

**Response Format:**
```json
{{
    "items": [],
    "total": 100,
    "page": 1,
    "per_page": 10,
    "pages": 10,
    "has_next": true,
    "has_prev": false
}}
```

## Error Handling

The API uses standard HTTP status codes and provides detailed error messages in the response body. Always check the status code and error message for proper error handling.

## SDKs and Libraries

Currently, the API can be consumed using any HTTP client. Official SDKs may be available in the future.

## Changelog

### Version 1.0.0
- Initial API release
- Basic CRUD operations
- Authentication system
- Health check endpoints
"""

        # Customize based on authentication type
        auth_section = self._get_auth_documentation()

        # Add CRUD endpoints documentation
        crud_endpoints = ""
        if self.config.project_type in [ProjectType.CRUD, ProjectType.API]:
            crud_endpoints = (
                self._get_crud_endpoints_docs()
            )  # Add project-specific endpoints

        project_specific_endpoints = ""
        if self.config.project_type == ProjectType.ML_API:
            project_specific_endpoints = self._get_ml_endpoints_docs()

        # Convert project name to PascalCase
        project_name_pascal = "".join(
            word.capitalize()
            for word in self.config.name.replace("-", " ").replace("_", " ").split()
        )

        return template.format(
            project_name=self.config.name,
            auth_section=auth_section,
            crud_endpoints=crud_endpoints,
            project_specific_endpoints=project_specific_endpoints,
            project_name_pascal=project_name_pascal,
        )

    def _get_auth_documentation(self) -> str:
        """Get authentication documentation"""
        if self.config.auth_type == AuthType.NONE:
            return "This API does not require authentication."

        elif self.config.auth_type == AuthType.JWT:
            return """The API uses JWT (JSON Web Token) for authentication.

#### Register
**POST /auth/register**

Register a new user account.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

#### Login
**POST /auth/token**

Authenticate and receive access token.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "SecurePassword123!"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

#### Using the Token

Include the token in the Authorization header for protected endpoints:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```"""

        elif self.config.auth_type == AuthType.API_KEY:
            return """The API uses API Key authentication.

Include your API key in the request header:
```
X-API-Key: your-api-key-here
```

Contact the administrator to obtain an API key."""

        elif self.config.auth_type == AuthType.OAUTH2:
            return """The API uses OAuth2 for authentication.

Please refer to the OAuth2 provider documentation for the authentication flow."""

        return ""

    def _get_crud_endpoints_docs(self) -> str:
        """Get CRUD endpoints documentation"""
        return """
### Items

#### GET /items
Get list of items with optional filtering and pagination.

**Query Parameters:**
- `search` (string): Search in item titles
- `category` (string): Filter by category
- `is_active` (boolean): Filter by active status
- `page` (integer): Page number
- `per_page` (integer): Items per page

**Response:**
```json
[
    {
        "id": 1,
        "title": "Sample Item",
        "description": "Item description",
        "price": 29.99,
        "category": "electronics",
        "is_active": true,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
]
```

#### POST /items
Create a new item.

**Request Body:**
```json
{
    "title": "New Item",
    "description": "Item description",
    "price": 29.99,
    "category": "electronics"
}
```

#### GET /items/{item_id}
Get item by ID.

**Response:**
```json
{
    "id": 1,
    "title": "Sample Item",
    "description": "Item description",
    "price": 29.99,
    "category": "electronics",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
```

#### PUT /items/{item_id}
Update item by ID.

**Request Body:**
```json
{
    "title": "Updated Item",
    "price": 39.99
}
```

#### DELETE /items/{item_id}
Delete item by ID.

**Response:** 204 No Content
"""

    def _get_ml_endpoints_docs(self) -> str:
        """Get ML endpoints documentation"""
        return """
### Machine Learning

#### POST /predict
Make a prediction using the ML model.

**Request Body:**
```json
{
    "features": {
        "feature1": 1.0,
        "feature2": 2.0,
        "feature3": 3.0
    },
    "model_version": "1.0.0"
}
```

**Response:**
```json
{
    "prediction": {
        "value": 0.85,
        "confidence": 0.92,
        "category": "positive"
    },
    "status": "success"
}
```

#### GET /model/info
Get information about the ML model.

**Response:**
```json
{
    "model_name": "DefaultModel",
    "version": "1.0.0",
    "description": "Machine Learning model for predictions"
}
```
"""

    def _get_deployment_docs_template(self) -> str:
        """Get deployment documentation template"""
        template = """# Deployment Guide

This guide covers different deployment options for {project_name_pascal}.

## Docker Deployment

### Prerequisites
- Docker and Docker Compose installed
- Git

### Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd {project_name_snake}
```

2. Copy environment variables:
```bash
cp .env.template .env
```

3. Update environment variables in `.env` file with production values.

4. Build and run with Docker Compose:
```bash
docker-compose up -d
```

The application will be available at `http://localhost:8000`.

### Production Docker Deployment

For production deployment, consider:

1. **Environment Variables**: Set proper production values
2. **Database**: Use a managed database service
3. **Reverse Proxy**: Use Nginx or similar
4. **SSL/TLS**: Configure HTTPS
5. **Logging**: Configure centralized logging
6. **Monitoring**: Set up health checks and monitoring

## Cloud Deployment

### AWS ECS

1. Build and push Docker image to ECR
2. Create ECS cluster and task definition
3. Configure load balancer and auto-scaling
4. Set up RDS for database

### Google Cloud Run

1. Build container image
2. Deploy to Cloud Run
3. Configure Cloud SQL for database
4. Set up custom domain and SSL

### Azure Container Instances

1. Create container registry
2. Deploy to Container Instances
3. Configure Azure Database
4. Set up Application Gateway

## Traditional Server Deployment

### Ubuntu/Debian

1. Install Python {python_version}:
```bash
sudo apt update
sudo apt install python{python_version} python{python_version}-venv
```

2. Create virtual environment:
```bash
python{python_version} -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export DATABASE_URL="your-database-url"
export SECRET_KEY="your-secret-key"
```

5. Run the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UnicornWorker --bind 0.0.0.0:8000
```

## Database Setup

{database_setup}

## Environment Variables

Required environment variables for production:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for JWT tokens (generate with `openssl rand -hex 32`)
- `DEBUG`: Set to `False` for production
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins

{additional_config}

## Health Checks

The application provides health check endpoints:
- `/health` - Application health
- `/api/v1/health` - API health

Use these for load balancer health checks.

## Backup and Recovery

### Database Backup

{backup_instructions}

### Application Backup

- Backup environment configuration
- Backup uploaded files (if any)
- Backup application logs

## Troubleshooting

### Common Issues

1. **Database Connection**: Check DATABASE_URL and network connectivity
2. **Permission Errors**: Ensure proper file permissions
3. **Port Already in Use**: Change port or stop conflicting service
4. **Memory Issues**: Increase server memory or optimize queries

### Logs

Check application logs:
```bash
docker-compose logs app
```

Or for traditional deployment:
```bash
tail -f /var/log/{project_name_snake}.log
```

## Security Considerations

1. **Use HTTPS** in production
2. **Keep dependencies updated**
3. **Use strong passwords** for database and admin accounts
4. **Implement rate limiting**
5. **Regular security audits**
6. **Backup encryption**

## Performance Optimization

1. **Database indexing**
2. **Connection pooling**
3. **Caching** (Redis)
4. **CDN** for static files
5. **Load balancing**
6. **Database read replicas**
"""

        # Customize database setup based on type
        database_setup = self._get_database_setup_docs()

        # Additional configuration
        additional_config = ""
        if self.config.include_celery:
            additional_config += "\n- `CELERY_BROKER_URL`: Redis URL for Celery\n- `CELERY_RESULT_BACKEND`: Redis URL for results"

        if self.config.include_monitoring:
            additional_config += "\n- `ENABLE_METRICS`: Enable Prometheus metrics\n- `METRICS_PORT`: Port for metrics endpoint"

        # Backup instructions
        backup_instructions = self._get_backup_instructions()

        project_name = self.config.name
        project_name_pascal = "".join(
            word.capitalize() for word in project_name.replace("-", "_").split("_")
        )
        project_name_pascal = "".join(
            word.capitalize() for word in project_name.replace("-", "_").split("_")
        )

        project_name_snake = (
            self.config.name.lower().replace("-", "_").replace(" ", "_")
        )

        return self.format_template(
            template.format(
                project_name=project_name,
                project_name_pascal=project_name_pascal,
                project_name_snake=project_name_snake,
                database_setup=database_setup,
                additional_config=additional_config,
                backup_instructions=backup_instructions,
                python_version=self.config.python_version,
            )
        )

    def _get_database_setup_docs(self) -> str:
        """Get database setup documentation"""
        if self.config.database_type.value == "postgresql":
            return """### PostgreSQL

1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE {project_name_snake};
CREATE USER {project_name_snake}_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE {project_name_snake} TO {project_name_snake}_user;
```

3. Set DATABASE_URL:
```
DATABASE_URL=postgresql://{project_name_snake}_user:password@localhost/{project_name_snake}
```"""

        elif self.config.database_type.value == "mysql":
            return """### MySQL

1. Install MySQL
2. Create database:
```sql
CREATE DATABASE {project_name_snake};
CREATE USER '{project_name_snake}_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON {project_name_snake}.* TO '{project_name_snake}_user'@'localhost';
```

3. Set DATABASE_URL:
```
DATABASE_URL=mysql://{project_name_snake}_user:password@localhost/{project_name_snake}
```"""

        elif self.config.database_type.value == "mongodb":
            return """### MongoDB

1. Install MongoDB
2. Create database and user:
```javascript
use {project_name_snake}
db.createUser({{
    user: "{project_name_snake}_user",
    pwd: "password",
    roles: ["readWrite"]
}})
```

3. Set DATABASE_URL:
```
DATABASE_URL=mongodb://{project_name_snake}_user:password@localhost:27017/{project_name_snake}
```"""

        elif self.config.database_type.value == "redis":
            return """### Redis

1. Install Redis
2. Configure Redis (optional authentication)
3. Set DATABASE_URL:
```
DATABASE_URL=redis://localhost:6379/0
```"""

        else:  # SQLite
            return """### SQLite

SQLite database will be created automatically. No additional setup required.
For production, consider using PostgreSQL or MySQL."""

    def _get_backup_instructions(self) -> str:
        """Get backup instructions"""
        if self.config.database_type.value == "postgresql":
            return """```bash
# Backup
pg_dump {project_name_snake} > backup.sql

# Restore
psql {project_name_snake} < backup.sql
```"""

        elif self.config.database_type.value == "mysql":
            return """```bash
# Backup
mysqldump {project_name_snake} > backup.sql

# Restore
mysql {project_name_snake} < backup.sql
```"""

        elif self.config.database_type.value == "mongodb":
            return """```bash
# Backup
mongodump --db {project_name_snake} --out backup/

# Restore
mongorestore backup/{project_name_snake}/
```"""

        else:
            return """```bash
# Backup SQLite
cp app.db backup/app_$(date +%Y%m%d_%H%M%S).db

# Restore
cp backup/app_20240101_120000.db app.db
```"""

    def _get_development_docs_template(self) -> str:
        """Get development documentation template"""
        template = """# Development Guide

This guide helps developers set up the development environment and contribute to {project_name_pascal}.

## Prerequisites

- Python {python_version} or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)
{additional_prereqs}

## Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd {project_name_snake}
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\\Scripts\\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
cp .env.template .env
```

Edit `.env` file with your local configuration.

### 5. Database Setup

{dev_database_setup}

### 6. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
{project_name_snake}/
├── app/
│   ├── api/                # API endpoints
│   │   └── v1/            # API version 1
│   ├── core/              # Core functionality
│   ├── db/                # Database configuration
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── main.py           # FastAPI application
├── tests/                 # Test files
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose
└── README.md             # Project README
```

## Development Workflow

### 1. Feature Development

1. Create feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make changes and add tests
3. Run tests locally
4. Commit and push changes
5. Create pull request

### 2. Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/api/test_endpoints.py

# Run with verbose output
pytest -v
```

### 3. Code Quality

```bash
# Format code with black
black app/ tests/

# Sort imports with isort
isort app/ tests/

# Lint with flake8
flake8 app/ tests/

# Type checking with mypy
mypy app/
```

## Database Migrations

{migration_section}

## Adding New Features

### 1. API Endpoints

1. Add endpoint to `app/api/v1/endpoints.py`
2. Create request/response schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Add tests in `tests/api/`

### 2. Database Models

1. Create model in `app/models/`
2. Create migration (if using Alembic)
3. Update schemas in `app/schemas/`
4. Add service functions in `app/services/`

### 3. Background Tasks

{background_tasks_section}

## Debugging

### 1. Debug Mode

Set `DEBUG=True` in `.env` for detailed error messages.

### 2. Logging

Configure logging in `app/utils/logging.py`:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Debug message")
```

### 3. Database Debugging

Enable SQL logging by setting `echo=True` in database configuration.

## Performance

### 1. Database Queries

- Use database indexes
- Avoid N+1 queries
- Use pagination for large datasets
- Consider database connection pooling

### 2. API Performance

- Use async/await for I/O operations
- Implement caching where appropriate
- Use background tasks for heavy operations
- Monitor API response times

## Common Development Tasks

### Adding Dependencies

1. Install package: `pip install package-name`
2. Update requirements: `pip freeze > requirements.txt`
3. Test locally
4. Commit requirements.txt

### Environment Variables

Add new environment variables to:
1. `app/core/config.py`
2. `.env.template`
3. Documentation

### API Versioning

When creating breaking changes:
1. Create new version directory: `app/api/v2/`
2. Update main.py to include new router
3. Maintain backward compatibility

## Troubleshooting

### Common Issues

1. **Import Errors**: Check PYTHONPATH and virtual environment
2. **Database Connection**: Verify DATABASE_URL and database status
3. **Port Already in Use**: Change port or stop conflicting process
4. **Permission Errors**: Check file permissions and ownership

### Getting Help

1. Check existing documentation
2. Search issues in repository
3. Create new issue with:
   - Error message
   - Steps to reproduce
   - Environment information
"""

        # Customize based on configuration
        additional_prereqs = ""
        if self.config.include_docker:
            additional_prereqs = (
                "- Docker and Docker Compose (for containerized development)"
            )

        dev_database_setup = (
            "For development, SQLite is used by default. No additional setup required."
        )
        if self.config.database_type.value != "sqlite":
            dev_database_setup = f"Set up {self.config.database_type.value} locally or use Docker:\n```bash\ndocker-compose up -d {self.config.database_type.value}\n```"

        migration_section = ""
        if self.config.is_advanced:
            migration_section = """Using Alembic for database migrations:

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1
```"""
        else:
            migration_section = "Database tables are created automatically on startup."

        background_tasks_section = ""
        if self.config.include_celery:
            background_tasks_section = """Add background tasks in `app/tasks/`:

```python
from celery import Celery

celery_app = Celery("tasks")

@celery_app.task
def background_task(data):
    # Task implementation
    return result
```"""
        else:
            background_tasks_section = (
                "Use FastAPI BackgroundTasks for simple background operations."
            )

        project_name = self.config.name
        project_name_pascal = "".join(
            word.capitalize() for word in project_name.replace("-", "_").split("_")
        )
        project_name_snake = (
            self.config.name.lower().replace("-", "_").replace(" ", "_")
        )

        return self.format_template(
            template.format(
                project_name=project_name,
                project_name_pascal=project_name_pascal,
                project_name_snake=project_name_snake,
                python_version=self.config.python_version,
                additional_prereqs=additional_prereqs,
                dev_database_setup=dev_database_setup,
                migration_section=migration_section,
                background_tasks_section=background_tasks_section,
            )
        )

    def _get_config_docs_template(self) -> str:
        """Get configuration documentation template"""
        template = """# Configuration Guide

This document describes all configuration options for {project_name_pascal}.

## Environment Variables

All configuration is done through environment variables, which can be set in a `.env` file.

### Application Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | string | `{project_name}` | Application name |
| `APP_VERSION` | string | `1.0.0` | Application version |
| `DEBUG` | boolean | `True` | Enable debug mode |
| `API_PREFIX` | string | `/api/v1` | API URL prefix |

### Server Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOST` | string | `0.0.0.0` | Server host |
| `PORT` | integer | `8000` | Server port |

### Database Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | string | `sqlite:///./app.db` | Database connection URL |

{auth_config}

### CORS Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ALLOWED_ORIGINS` | list | `["http://localhost:3000"]` | Allowed CORS origins |

### Logging Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | `INFO` | Logging level |
| `LOG_FILE` | string | `None` | Log file path (optional) |

{additional_settings}

## Database URLs

### SQLite
```
DATABASE_URL=sqlite:///./app.db
```

### PostgreSQL
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### MySQL
```
DATABASE_URL=mysql://user:password@localhost:3306/dbname
```

### MongoDB
```
DATABASE_URL=mongodb://user:password@localhost:27017/dbname
```

### Redis
```
DATABASE_URL=redis://localhost:6379/0
```

## Security Configuration

### Secret Key

Generate a secure secret key:
```bash
openssl rand -hex 32
```

Set in environment:
```
SECRET_KEY=your-generated-secret-key
```

### CORS Configuration

For production, specify exact origins:
```
ALLOWED_ORIGINS=["https://yourdomain.com", "https://app.yourdomain.com"]
```

{auth_security}

## Environment-Specific Configuration

### Development
```env
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./dev.db
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### Testing
```env
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./test.db
```

### Production
```env
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:password@db-server:5432/prod_db
SECRET_KEY=your-secure-secret-key
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

## Configuration Validation

The application validates configuration on startup. Common validation errors:

1. **Invalid DATABASE_URL**: Check connection string format
2. **Missing SECRET_KEY**: Required for JWT authentication
3. **Invalid LOG_LEVEL**: Must be DEBUG, INFO, WARNING, ERROR, or CRITICAL
4. **Invalid CORS origins**: Must be valid URLs

## Performance Configuration

### Database Connection Pooling

For production databases, consider connection pooling:

```env
# PostgreSQL with connection pool
DATABASE_URL=postgresql://user:pass@host:5432/db?pool_size=20&max_overflow=0
```

### Uvicorn Configuration

Production server configuration:
```bash
uvicorn app.main:app \\
  --host 0.0.0.0 \\
  --port 8000 \\
  --workers 4 \\
  --access-log \\
  --log-level info
```

{monitoring_config}

## Troubleshooting Configuration

### Common Issues

1. **Environment variables not loaded**: Check `.env` file location and syntax
2. **Database connection failed**: Verify DATABASE_URL and database server status
3. **CORS errors**: Check ALLOWED_ORIGINS includes your frontend domain
4. **Authentication errors**: Verify SECRET_KEY is set and consistent

### Configuration Testing

Test configuration with:
```python
from app.core.config import settings
print(f"Database: {{settings.DATABASE_URL}}")
print(f"Debug mode: {{settings.DEBUG}}")
```
"""

        # Customize based on authentication
        auth_config = ""
        auth_security = ""
        if self.config.auth_type != AuthType.NONE:
            auth_config = """
### Authentication Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SECRET_KEY` | string | Required | Secret key for JWT tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | integer | `30` | Token expiration time |
| `ALGORITHM` | string | `HS256` | JWT algorithm |"""

            auth_security = """
### Authentication Security

1. **Use strong SECRET_KEY** (at least 32 characters)
2. **Set appropriate token expiration**
3. **Use HTTPS in production**
4. **Implement token refresh** for long-lived applications"""

        # Additional settings
        additional_settings = ""
        if self.config.include_monitoring:
            additional_settings += """
### Monitoring Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENABLE_METRICS` | boolean | `True` | Enable Prometheus metrics |
| `METRICS_PORT` | integer | `9090` | Metrics server port |"""

        if self.config.include_celery:
            additional_settings += """
### Celery Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CELERY_BROKER_URL` | string | `redis://localhost:6379/0` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | string | `redis://localhost:6379/0` | Celery result backend |"""

        monitoring_config = ""
        if self.config.include_monitoring:
            monitoring_config = """
## Monitoring Configuration

### Prometheus Metrics

Metrics endpoint: `http://localhost:8000/metrics`

Available metrics:
- Request count and duration
- Database connection pool status
- Background task metrics

### Health Checks

Configure health check intervals:
```
HEALTH_CHECK_INTERVAL=30  # seconds
```"""

        return template.format(
            auth_config=auth_config,
            auth_security=auth_security,
            additional_settings=additional_settings,
            monitoring_config=monitoring_config,
            project_name=self.config.name,
            project_name_pascal="".join(
                word.capitalize()
                for word in self.config.name.replace("-", "_").split("_")
            ),
            python_version=self.config.python_version,
            project_name_snake=self.config.name.lower()
            .replace("-", "_")
            .replace(" ", "_"),
        )

    def _get_contributing_template(self) -> str:
        """Get contributing guide template"""
        template = """# Contributing to {project_name_pascal}

Thank you for your interest in contributing to {project_name_pascal}! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

Please refer to the [Development Guide](docs/development.md) for detailed setup instructions.

## Contribution Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Write descriptive variable and function names
- Keep functions small and focused

### Testing

- Write tests for new features
- Ensure all tests pass before submitting
- Aim for high test coverage (>80%)
- Include both unit tests and integration tests

### Documentation

- Update documentation for new features
- Include docstrings for all functions and classes
- Update API documentation if needed
- Keep README.md up to date

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add user authentication system
fix: resolve database connection issue
docs: update API documentation
test: add tests for item service
refactor: improve error handling
```

### Pull Requests

1. **Create descriptive PR title**
2. **Include detailed description** of changes
3. **Reference related issues** (if any)
4. **Ensure CI passes**
5. **Request review** from maintainers

#### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)
```

## Issue Reporting

### Bug Reports

Include the following information:

1. **Environment**: OS, Python version, dependencies
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Error messages** (if any)
6. **Minimal code example**

### Feature Requests

Include:

1. **Problem description**
2. **Proposed solution**
3. **Alternative solutions considered**
4. **Additional context**

## Code Review Process

1. **Automated checks** must pass
2. **At least one maintainer** must review
3. **Address feedback** promptly
4. **Squash commits** before merge (if requested)

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run linting
flake8 app/ tests/

# Format code
black app/ tests/
isort app/ tests/
```

## API Changes

For API changes:

1. **Maintain backward compatibility** when possible
2. **Version breaking changes** appropriately
3. **Update documentation**
4. **Include migration guide** (if needed)

## Dependencies

- **Minimize new dependencies**
- **Use well-maintained packages**
- **Pin versions** in requirements.txt
- **Document dependency rationale**

## Security

- **Report security issues privately** to maintainers
- **Follow security best practices**
- **Keep dependencies updated**
- **Review code for security implications**

## Community Guidelines

- **Be respectful** and inclusive
- **Provide constructive feedback**
- **Help others learn**
- **Follow code of conduct**

## Recognition

Contributors are recognized in:
- Repository contributors list
- Release notes (for significant contributions)
- Project documentation

## Questions?

- Check existing documentation
- Search existing issues
- Create new issue for questions
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Thank You!

Your contributions make this project better for everyone. Thank you for taking the time to contribute!
"""

        return self.format_template(template)
