"""Template management for Fast Starter"""

import os
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, Template

from .core.config import ProjectConfig


class TemplateManager:
    """Manages template loading and rendering"""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.template_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_template(self, template_name: str, **kwargs) -> str:
        """Render a template with the given context"""
        template = self.env.get_template(template_name)
        context = self._get_base_context()
        context.update(kwargs)
        return template.render(**context)

    def _get_base_context(self) -> Dict[str, Any]:
        """Get base template context with project configuration"""
        return {
            "project_name": self.config.name,
            "project_name_snake": self.config.name.lower().replace("-", "_"),
            "project_name_pascal": "".join(
                word.capitalize()
                for word in self.config.name.replace("-", "_").split("_")
            ),
            "project_type": self.config.project_type.value,
            "database_type": self.config.database_type.value,
            "auth_type": self.config.auth_type.value,
            "is_async": self.config.is_async,
            "is_advanced": self.config.is_advanced,
            "include_docker": self.config.include_docker,
            "include_tests": self.config.include_tests,
            "include_docs": self.config.include_docs,
            "include_monitoring": self.config.include_monitoring,
            "include_celery": self.config.include_celery,
            "python_version": self.config.python_version,
        }
