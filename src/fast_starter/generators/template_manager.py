"""
Template Manager
Manages templates for project generation
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from ..core.config import ProjectConfig
import logging

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages templates for project generation"""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.env = self._setup_jinja_environment()

    def _setup_jinja_environment(self) -> Environment:
        """Setup Jinja2 environment"""
        if self.templates_dir.exists():
            loader = FileSystemLoader(str(self.templates_dir))
        else:
            # Fallback to a simple loader if templates directory doesn't exist
            loader = FileSystemLoader(".")

        env = Environment(
            loader=loader,
            autoescape=False,
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        env.filters["snake_case"] = self._to_snake_case
        env.filters["pascal_case"] = self._to_pascal_case
        env.filters["kebab_case"] = self._to_kebab_case

        return env

    def _to_snake_case(self, value: str) -> str:
        """Convert string to snake_case"""
        return value.lower().replace("-", "_").replace(" ", "_")

    def _to_pascal_case(self, value: str) -> str:
        """Convert string to PascalCase"""
        return "".join(word.capitalize() for word in value.replace("-", "_").split("_"))

    def _to_kebab_case(self, value: str) -> str:
        """Convert string to kebab-case"""
        return value.lower().replace("_", "-").replace(" ", "-")

    def get_template_vars(self) -> Dict[str, Any]:
        """Get template variables for rendering"""
        return {
            "project_name": self.config.name,
            "project_name_snake": self._to_snake_case(self.config.name),
            "project_name_pascal": self._to_pascal_case(self.config.name),
            "project_name_kebab": self._to_kebab_case(self.config.name),
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

    def render_template(
        self, template_name: str, extra_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render a template with variables"""
        try:
            template = self.env.get_template(template_name)
            vars_dict = self.get_template_vars()

            if extra_vars:
                vars_dict.update(extra_vars)

            return template.render(**vars_dict)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            raise

    def render_string(
        self, template_string: str, extra_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render a template string with variables"""
        try:
            template = Template(template_string)
            vars_dict = self.get_template_vars()

            if extra_vars:
                vars_dict.update(extra_vars)

            return template.render(**vars_dict)
        except Exception as e:
            logger.error(f"Failed to render template string: {e}")
            raise

    def template_exists(self, template_name: str) -> bool:
        """Check if a template file exists"""
        try:
            self.env.get_template(template_name)
            return True
        except:
            return False

    def list_templates(self) -> list:
        """List all available templates"""
        if not self.templates_dir.exists():
            return []

        templates = []
        for root, dirs, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith((".j2", ".jinja", ".template")):
                    rel_path = os.path.relpath(
                        os.path.join(root, file), self.templates_dir
                    )
                    templates.append(rel_path)

        return templates
