"""
Base Generator Class
Provides common functionality for all generators
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

from .config import ProjectConfig, logger


class BaseGenerator(ABC):
    """Base class for all file generators"""

    def __init__(self, config: ProjectConfig):
        self.config = config

    def should_generate(self) -> bool:
        """Determine if this generator should run based on configuration"""
        return True

    @abstractmethod
    def generate(self):
        """Generate the files for this component"""
        pass

    def write_file(self, file_path: str, content: str):
        """Write content to a file, creating directories if needed"""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def get_template_vars(self) -> Dict[str, Any]:
        """Get template variables for string formatting"""
        return {
            "project_name": self.config.name,
            "project_name_snake": self.config.name.lower().replace("-", "_"),
            "project_name_pascal": "".join(
                word.capitalize()
                for word in self.config.name.replace("-", "_").split("_")
            ),
            "is_async": self.config.is_async,
            "is_advanced": self.config.is_advanced,
            "database_type": self.config.database_type.value,
            "auth_type": self.config.auth_type.value,
            "python_version": self.config.python_version,
            "include_docker": self.config.include_docker,
            "include_tests": self.config.include_tests,
            "include_docs": self.config.include_docs,
            "include_monitoring": self.config.include_monitoring,
            "include_celery": self.config.include_celery,
        }

    def format_template(self, template: str) -> str:
        """Format a template string with project variables"""
        return template.format(**self.get_template_vars())
