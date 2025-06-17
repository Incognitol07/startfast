"""
Main Project Generator
Orchestrates the creation of FastAPI projects
"""

import os
import shutil
from typing import Dict, Any
from pathlib import Path

from .base_generator import BaseGenerator
from .file_generators import *
from .file_generators.environment_generator import EnvironmentGenerator
from .template_manager import TemplateManager
from .config import ProjectConfig, logger


class ProjectGenerator(BaseGenerator):
    """Main project generator that orchestrates the entire project creation"""

    def __init__(self, config: ProjectConfig):
        super().__init__(config)
        self.template_manager = TemplateManager(config)
        self._setup_generators()

    def _setup_generators(self):
        """Initialize all file generators"""
        self.generators = {
            "requirements": RequirementsGenerator(self.config),
            "environment": EnvironmentGenerator(self.config),
            "main": MainAppGenerator(self.config),
            "config": ConfigGenerator(self.config),
            "database": DatabaseGenerator(self.config),
            "auth": AuthGenerator(self.config),
            "api": APIGenerator(self.config),
            "models": ModelsGenerator(self.config),
            "schemas": SchemasGenerator(self.config),
            "services": ServicesGenerator(self.config),
            "utils": UtilsGenerator(self.config),
            "docker": DockerGenerator(self.config),
            "tests": TestsGenerator(self.config),
            "docs": DocsGenerator(self.config),
        }

        if self.config.include_monitoring:
            self.generators["monitoring"] = MonitoringGenerator(self.config)

        if self.config.include_celery:
            self.generators["celery"] = CeleryGenerator(self.config)

    def generate(self):
        """Generate the complete project"""
        logger.info(f"🏗️  Generating FastAPI project: {self.config.name}")

        # Create project directory structure
        self._create_directory_structure()

        # Generate all files
        self._generate_files()

        # Post-generation setup
        self._post_generation_setup()

    def _create_directory_structure(self):
        """Create the basic directory structure"""
        logger.info("📁 Creating directory structure...")

        # Remove existing directory if it exists
        if os.path.exists(self.config.path):
            shutil.rmtree(self.config.path)

        # Create main directories
        directories = [
            self.config.path,
            f"{self.config.path}/app",
            f"{self.config.path}/app/api",
            f"{self.config.path}/app/api/v1",
            f"{self.config.path}/app/core",
            f"{self.config.path}/app/db",
            f"{self.config.path}/app/models",
            f"{self.config.path}/app/schemas",
            f"{self.config.path}/app/services",
            f"{self.config.path}/app/utils",
        ]

        # Add optional directories
        if self.config.include_tests:
            directories.extend(
                [
                    f"{self.config.path}/tests",
                    f"{self.config.path}/tests/api",
                    f"{self.config.path}/tests/services",
                ]
            )

        if self.config.include_docs:
            directories.append(f"{self.config.path}/docs")

        if self.config.include_celery:
            directories.append(f"{self.config.path}/app/tasks")

        # Create all directories
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _generate_files(self):
        """Generate all project files"""
        logger.info("📝 Generating project files...")

        for name, generator in self.generators.items():
            if generator.should_generate():
                logger.info(f"  ⚡ Generating {name} files...")
                generator.generate()

    def _post_generation_setup(self):
        """Perform post-generation setup tasks"""
        logger.info("🔧 Performing post-generation setup...")

        # Create __init__.py files
        self._create_init_files()

        # Generate README
        self._generate_readme()

        # Generate .gitignore
        self._generate_gitignore()

        # Generate .env template
        self._generate_env_template()

    def _create_init_files(self):
        """Create __init__.py files for Python packages"""
        init_files = [
            f"{self.config.path}/app/__init__.py",
            f"{self.config.path}/app/api/__init__.py",
            f"{self.config.path}/app/api/v1/__init__.py",
            f"{self.config.path}/app/core/__init__.py",
            f"{self.config.path}/app/db/__init__.py",
            f"{self.config.path}/app/models/__init__.py",
            f"{self.config.path}/app/schemas/__init__.py",
            f"{self.config.path}/app/services/__init__.py",
            f"{self.config.path}/app/utils/__init__.py",
        ]

        if self.config.include_tests:
            init_files.extend(
                [
                    f"{self.config.path}/tests/__init__.py",
                    f"{self.config.path}/tests/api/__init__.py",
                    f"{self.config.path}/tests/services/__init__.py",
                ]
            )

        if self.config.include_celery:
            init_files.append(f"{self.config.path}/app/tasks/__init__.py")

        for init_file in init_files:
            Path(init_file).touch()

    def _generate_readme(self):
        """Generate project README"""
        readme_content = self.template_manager.get_readme_template()
        self.write_file(f"{self.config.path}/README.md", readme_content)

    def _generate_gitignore(self):
        """Generate .gitignore file"""
        gitignore_content = self.template_manager.get_gitignore_template()
        self.write_file(f"{self.config.path}/.gitignore", gitignore_content)

    def _generate_env_template(self):
        """Generate .env.template file"""
        env_content = self.template_manager.get_env_template()
        self.write_file(f"{self.config.path}/.env.template", env_content)
