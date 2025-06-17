"""
Fast Starter - A comprehensive FastAPI project generator

This package provides tools to generate scalable, modular FastAPI projects
with various configurations including different databases, authentication
methods, and project structures.
"""

__version__ = "0.1.0"
__author__ = "FastStarter Team"
__email__ = "contact@faststarter.dev"

from .core.config import ProjectConfig, ProjectType, DatabaseType, AuthType
from .generators.project_generator import ProjectGenerator

__all__ = [
    "ProjectConfig",
    "ProjectType",
    "DatabaseType",
    "AuthType",
    "ProjectGenerator",
]
