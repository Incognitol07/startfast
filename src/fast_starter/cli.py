"""
CLI module for Fast Starter
Command line interface for generating FastAPI projects
"""

import argparse
import os
import sys
import logging
from typing import Optional

from .core.config import ProjectConfig, ProjectType, DatabaseType, AuthType
from .generators.project_generator import ProjectGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="Fast Starter - Generate scalable FastAPI projects",
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

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser


def create_project_config(args) -> ProjectConfig:
    """Create project configuration from arguments"""
    project_path = os.path.join(args.path, args.name)

    # Handle existing directory
    if os.path.exists(project_path) and not args.force:
        try:
            confirm = input(
                f"Directory '{project_path}' already exists. Overwrite? (y/N): "
            )
            if confirm.lower() != "y":
                logger.info("Operation cancelled.")
                sys.exit(0)
        except KeyboardInterrupt:
            logger.info("\nOperation cancelled.")
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


def main():
    """Main entry point for the CLI"""
    try:
        parser = create_argument_parser()
        args = parser.parse_args()

        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Create project configuration
        config = create_project_config(args)

        # Generate project
        logger.info(f"🚀 Starting FastAPI project generation: {config.name}")
        generator = ProjectGenerator(config)
        generator.generate()

        # Success message
        logger.info(f"✅ FastAPI project '{config.name}' created successfully!")
        logger.info(f"📁 Location: {config.path}")
        logger.info(f"🔧 Type: {config.project_type.value}")
        logger.info(f"💾 Database: {config.database_type.value}")
        logger.info(f"🔐 Auth: {config.auth_type.value}")

        # Next steps
        logger.info("\n🎯 Next steps:")
        logger.info(f"   cd {config.name}")
        logger.info("   pip install -r requirements.txt")
        logger.info("   uvicorn app.main:app --reload")

    except KeyboardInterrupt:
        logger.info("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error generating project: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
