"""
CLI module for StartFast
Command line interface for generating FastAPI projects
"""

import argparse
import os
import sys
import logging
from typing import Optional, Dict, Any, List, Tuple

# Add colorama for cross-platform colored terminal output
try:
    from colorama import init, Fore, Back, Style

    init(autoreset=True)  # Initialize colorama
    HAS_COLORAMA = True
except ImportError:
    # Fallback if colorama is not installed
    HAS_COLORAMA = False

    class Fore:
        GREEN = YELLOW = BLUE = CYAN = RED = MAGENTA = WHITE = ""

    class Back:
        GREEN = YELLOW = BLUE = CYAN = RED = MAGENTA = WHITE = ""

    class Style:
        BRIGHT = DIM = RESET_ALL = ""


from .core.config import ProjectConfig, ProjectType, DatabaseType, AuthType
from .generators.project_generator import ProjectGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="StartFast - Generate scalable FastAPI projects",
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

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Launch interactive mode for configuration",
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


# Print the StartFast banner
def print_banner():
    """Print the StartFast banner"""
    width = 65
    title = "⚡ StartFast"
    subtitle = "Generate scalable FastAPI projects"

    banner = f"""{Fore.CYAN}{Style.BRIGHT}
╔{'═' * width}╗
║ {'⚡ StartFast'.center(width - 2)}║
║{subtitle.center(width)}║
╚{'═' * width}╝
{Style.RESET_ALL}
"""
    print(banner)


def print_colored(text: str, color: str = Fore.WHITE, style: str = "") -> None:
    """Print colored text with optional styling"""
    print(f"{style}{color}{text}{Style.RESET_ALL}")


def get_user_input(prompt: str, default: str = "", color: str = Fore.CYAN) -> str:
    """Get user input with colored prompt"""
    if default:
        display_prompt = f"{color}{prompt} [{default}]: {Style.RESET_ALL}"
    else:
        display_prompt = f"{color}{prompt}: {Style.RESET_ALL}"

    try:
        response = input(display_prompt).strip()
        return response if response else default
    except KeyboardInterrupt:
        print_colored("\n❌ Operation cancelled by user.", Fore.RED)
        sys.exit(0)


def get_choice(prompt: str, choices: List[Tuple[str, str]], default: str = "") -> str:
    """Get user choice from a list of options"""
    print_colored(f"\n{prompt}", Fore.YELLOW, Style.BRIGHT)
    print_colored("─" * 50, Fore.YELLOW)

    # Display choices with numbers
    for i, (value, description) in enumerate(choices, 1):
        indicator = (
            f"{Fore.GREEN}[DEFAULT]{Style.RESET_ALL} " if value == default else ""
        )
        print_colored(f"  {i}. {indicator}{description} ({value})", Fore.WHITE)

    while True:
        try:
            choice = get_user_input(
                "Select option",
                (
                    "1"
                    if not default
                    else str(
                        next(
                            (i for i, (v, _) in enumerate(choices, 1) if v == default),
                            1,
                        )
                    )
                ),
            )

            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1][0]

            # Try to match by value
            for value, _ in choices:
                if choice.lower() == value.lower():
                    return value

            print_colored("❌ Invalid choice. Please try again.", Fore.RED)

        except (ValueError, IndexError):
            print_colored(
                "❌ Invalid input. Please enter a number or option value.", Fore.RED
            )


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input from user"""
    default_text = "Y/n" if default else "y/N"
    while True:
        response = get_user_input(
            f"{prompt} ({default_text})", "y" if default else "n"
        ).lower()
        if response in ["y", "yes", "true", "1"]:
            return True
        elif response in ["n", "no", "false", "0"]:
            return False
        elif response == "":
            return default
        else:
            print_colored("❌ Please enter 'y' for yes or 'n' for no.", Fore.RED)


def interactive_config() -> ProjectConfig:
    """Interactive configuration mode"""
    print_banner()
    print_colored("🎯 Welcome to Interactive Mode!", Fore.GREEN, Style.BRIGHT)
    print_colored("Let's configure your FastAPI project step by step.\n", Fore.WHITE)

    # Project name
    print_colored("📝 PROJECT DETAILS", Fore.MAGENTA, Style.BRIGHT)
    print_colored("─" * 30, Fore.MAGENTA)

    name = ""
    while not name:
        name = get_user_input("Project name")
        if not name:
            print_colored(
                "❌ Project name cannot be empty. Please try again.", Fore.RED
            )

    # Project path
    path = get_user_input("Project directory", ".")
    project_path = os.path.join(path, name)

    # Check if directory exists
    if os.path.exists(project_path):
        overwrite = get_yes_no(
            f"Directory '{project_path}' already exists. Overwrite?", False
        )
        if not overwrite:
            print_colored("Operation cancelled.", Fore.YELLOW)
            sys.exit(0)

    # Project type
    project_type_choices = [
        (ProjectType.API.value, "Simple REST API - Basic CRUD operations"),
        (ProjectType.CRUD.value, "Full CRUD API - Complete database operations"),
        (ProjectType.ML_API.value, "Machine Learning API - ML model serving"),
        (
            ProjectType.MICROSERVICE.value,
            "Microservice - Service-oriented architecture",
        ),
    ]
    project_type = get_choice(
        "🚀 Select project type:", project_type_choices, ProjectType.API.value
    )

    # Database type
    database_choices = [
        (DatabaseType.SQLITE.value, "SQLite - Lightweight file-based database"),
        (DatabaseType.POSTGRESQL.value, "PostgreSQL - Advanced relational database"),
        (DatabaseType.MYSQL.value, "MySQL - Popular relational database"),
        (DatabaseType.MONGODB.value, "MongoDB - Document-based NoSQL database"),
        (DatabaseType.REDIS.value, "Redis - In-memory data structure store"),
    ]
    database_type = get_choice(
        "💾 Select database type:", database_choices, DatabaseType.SQLITE.value
    )

    # Authentication type
    auth_choices = [
        (AuthType.JWT.value, "JWT - JSON Web Tokens"),
        (AuthType.OAUTH2.value, "OAuth2 - OAuth2 with scopes"),
        (AuthType.API_KEY.value, "API Key - Simple API key authentication"),
        (AuthType.NONE.value, "None - No authentication"),
    ]
    auth_type = get_choice(
        "🔐 Select authentication method:", auth_choices, AuthType.JWT.value
    )

    # Advanced options
    print_colored("\n⚙️  ADVANCED OPTIONS", Fore.MAGENTA, Style.BRIGHT)
    print_colored("─" * 30, Fore.MAGENTA)

    is_async = get_yes_no("Use async/await pattern?", True)
    is_advanced = get_yes_no("Include advanced features?", False)

    # Optional features
    print_colored("\n🎁 OPTIONAL FEATURES", Fore.MAGENTA, Style.BRIGHT)
    print_colored("─" * 30, Fore.MAGENTA)

    include_docker = get_yes_no("Include Docker configuration?", True)
    include_tests = get_yes_no("Include test setup?", True)
    include_docs = get_yes_no("Include documentation setup?", True)
    include_monitoring = get_yes_no("Include monitoring tools?", False)
    include_celery = get_yes_no("Include Celery for background tasks?", False)

    # Python version
    python_version = get_user_input("Python version", "3.11")

    # Configuration summary
    print_colored("\n📋 CONFIGURATION SUMMARY", Fore.GREEN, Style.BRIGHT)
    print_colored("═" * 50, Fore.GREEN)
    print_colored(f"Project Name:     {name}", Fore.WHITE)
    print_colored(f"Location:         {project_path}", Fore.WHITE)
    print_colored(f"Type:             {project_type}", Fore.WHITE)
    print_colored(f"Database:         {database_type}", Fore.WHITE)
    print_colored(f"Authentication:   {auth_type}", Fore.WHITE)
    print_colored(f"Async/Await:      {'Yes' if is_async else 'No'}", Fore.WHITE)
    print_colored(f"Advanced:         {'Yes' if is_advanced else 'No'}", Fore.WHITE)
    print_colored(f"Docker:           {'Yes' if include_docker else 'No'}", Fore.WHITE)
    print_colored(f"Tests:            {'Yes' if include_tests else 'No'}", Fore.WHITE)
    print_colored(f"Documentation:    {'Yes' if include_docs else 'No'}", Fore.WHITE)
    print_colored(
        f"Monitoring:       {'Yes' if include_monitoring else 'No'}", Fore.WHITE
    )
    print_colored(f"Celery:           {'Yes' if include_celery else 'No'}", Fore.WHITE)
    print_colored(f"Python Version:   {python_version}", Fore.WHITE)
    print_colored("═" * 50, Fore.GREEN)

    # Confirmation
    if not get_yes_no("\nProceed with this configuration?", True):
        print_colored("Operation cancelled.", Fore.YELLOW)
        sys.exit(0)

    return ProjectConfig(
        name=name,
        path=project_path,
        project_type=ProjectType(project_type),
        database_type=DatabaseType(database_type),
        auth_type=AuthType(auth_type),
        is_async=is_async,
        is_advanced=is_advanced,
        include_docker=include_docker,
        include_tests=include_tests,
        include_docs=include_docs,
        include_monitoring=include_monitoring,
        include_celery=include_celery,
        python_version=python_version,
    )


def main():
    """Main entry point for the CLI"""
    try:
        parser = create_argument_parser()
        args = parser.parse_args()

        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Check if interactive mode is requested
        if args.interactive:
            config = interactive_config()
        else:
            # Create project configuration from command line arguments
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
