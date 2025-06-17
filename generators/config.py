"""
Configuration classes and enums for FastStarter project generator
"""

import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ProjectType(Enum):
    """Available project types"""

    API = "api"
    CRUD = "crud"
    ML_API = "ml-api"
    MICROSERVICE = "microservice"


class DatabaseType(Enum):
    """Database options"""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"


class AuthType(Enum):
    """Authentication options"""

    NONE = "none"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api-key"


@dataclass
class ProjectConfig:
    """Configuration for project generation"""

    name: str
    path: str
    project_type: ProjectType
    database_type: DatabaseType
    auth_type: AuthType
    is_async: bool = True
    is_advanced: bool = False
    include_docker: bool = True
    include_tests: bool = True
    include_docs: bool = True
    include_monitoring: bool = False
    include_celery: bool = False
    python_version: str = "3.11"
