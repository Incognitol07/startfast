#!/usr/bin/env python3
"""
FastStarter - A comprehensive FastAPI project generator
Creates scalable, modular FastAPI projects with various configurations
"""

import argparse
import os
import sys

# Add the current directory to sys.path to enable imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generators.config import ProjectConfig, ProjectType, DatabaseType, AuthType, logger


def main():
    """Main entry point"""
    from generators.project_generator import ProjectGenerator

    parser = create_argument_parser()
    args = parser.parse_args()

    # Create project configuration
    config = create_project_config(args)

    # Generate project
    generator = ProjectGenerator(config)
    generator.generate()

    logger.info(f"🚀 FastAPI project '{config.name}' created successfully!")
    logger.info(f"📁 Location: {config.path}")
    logger.info(f"🔧 Type: {config.project_type.value}")
    logger.info(f"💾 Database: {config.database_type.value}")
    logger.info(f"🔐 Auth: {config.auth_type.value}")


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="FastStarter - Generate scalable FastAPI projects",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Required arguments
    parser.add_argument("name", help="Project name")

    parser.add_argument(
        "--path", default=".", help="Directory where project will be created"
    )

    # Project type
    parser.add_argument(
        "--type",
        choices=[t.value for t in ProjectType],
        default=ProjectType.API.value,
        help="Type of FastAPI project to generate",
    )

    # Database options
    parser.add_argument(
        "--database",
        choices=[db.value for db in DatabaseType],
        default=DatabaseType.SQLITE.value,
        help="Database type",
    )

    # Authentication
    parser.add_argument(
        "--auth",
        choices=[auth.value for auth in AuthType],
        default=AuthType.JWT.value,
        help="Authentication method",
    )

    # Configuration flags
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Generate synchronous version (default is async)",
    )

    parser.add_argument(
        "--advanced",
        action="store_true",
        help="Include advanced features and configurations",
    )

    parser.add_argument(
        "--no-docker", action="store_true", help="Skip Docker configuration"
    )

    parser.add_argument("--no-tests", action="store_true", help="Skip test setup")

    parser.add_argument(
        "--no-docs", action="store_true", help="Skip documentation setup"
    )

    parser.add_argument(
        "--monitoring",
        action="store_true",
        help="Include monitoring and observability tools",
    )

    parser.add_argument(
        "--celery", action="store_true", help="Include Celery for background tasks"
    )

    parser.add_argument(
        "--python-version", default="3.11", help="Python version for the project"
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing directory without confirmation",
    )

    return parser


def create_project_config(args) -> ProjectConfig:
    """Create project configuration from arguments"""
    project_path = os.path.join(args.path, args.name)

    # Handle existing directory
    if os.path.exists(project_path) and not args.force:
        confirm = input(
            f"Directory '{project_path}' already exists. Overwrite? (y/N): "
        )
        if confirm.lower() != "y":
            logger.info("Operation cancelled.")
            sys.exit(0)

    return ProjectConfig(
        name=args.name,
        path=project_path,
        project_type=ProjectType(args.type),
        database_type=DatabaseType(args.database),
        auth_type=AuthType(args.auth),
        is_async=not args.sync,
        is_advanced=args.advanced,
        include_docker=not args.no_docker,
        include_tests=not args.no_tests,
        include_docs=not args.no_docs,
        include_monitoring=args.monitoring,
        include_celery=args.celery,
        python_version=args.python_version,
    )


if __name__ == "__main__":
    main()
