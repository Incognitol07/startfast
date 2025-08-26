"""
CLI module for StartFast with Rich UI
Command line interface for generating FastAPI projects with beautiful, interactive UI
"""

import argparse
import os
import sys
import logging
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

# Rich imports for beautiful CLI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich import box
import time

from .core.config import ProjectConfig, ProjectType, DatabaseType, AuthType
from .generators.project_generator import ProjectGenerator

# Initialize Rich console
console = Console()
# Configure logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[logging.StreamHandler(console.file)]
)
logger = logging.getLogger("startfast")


class StartFastCLI:
    """Rich-powered CLI for StartFast"""
    
    def __init__(self):
        self.console = console
        
    def create_argument_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser"""
        parser = argparse.ArgumentParser(
            description="StartFast - Generate scalable FastAPI projects",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        # Required arguments
        parser.add_argument("name", nargs='?', help="Project name (optional in interactive mode)")

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
            "--no-interactive",
            action="store_true",
            help="Disable interactive mode (interactive is default)",
        )

        return parser

    def show_welcome_banner(self):
        """Display the gorgeous welcome banner"""
        title = Text("⚡ StartFast", style="bold bright_cyan")
        subtitle = Text("The Django-admin startproject for FastAPI", style="italic dim white")
        
        banner_content = Align.center(
            Panel(
                Align.center(f"{title}\n{subtitle}"),
                box=box.DOUBLE,
                padding=(1, 2),
                style="bright_cyan",
                title="[bold white]Welcome[/]",
                title_align="center"
            )
        )
        
        console.print()
        console.print(banner_content)
        console.print()
        
        # Show feature highlights
        features = [
            "🎯 Interactive Configuration",
            "🏗️ Multiple Project Types", 
            "💾 Database Integration",
            "🔐 Authentication Ready",
            "🐳 Docker Support",
            "📊 Monitoring & Observability"
        ]
        
        feature_columns = Columns(
            [f"[bright_green]{feature}[/]" for feature in features],
            equal=True,
            expand=True
        )
        
        console.print(Panel(
            feature_columns,
            title="[bold bright_blue]✨ Features[/]",
            box=box.ROUNDED,
            padding=(0, 1)
        ))
        console.print()

    def create_project_config_from_args(self, args) -> ProjectConfig:
        """Create project configuration from arguments"""
        if not args.name:
            console.print("[bold red]❌ Project name is required when not using interactive mode[/]")
            console.print("💡 Use interactive mode: [bold cyan]startfast[/] or [bold cyan]startfast --interactive[/]")
            sys.exit(1)
            
        project_path = os.path.join(args.path, args.name)

        # Handle existing directory
        if os.path.exists(project_path) and not args.force:
            overwrite = Confirm.ask(
                f"[yellow]Directory '{project_path}' already exists. Overwrite?[/]",
                default=False
            )
            if not overwrite:
                console.print("[yellow]📦 Operation cancelled.[/]")
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

    def get_project_name(self) -> str:
        """Get project name with validation"""
        while True:
            name = Prompt.ask(
                "\n[bold bright_blue]📝 What's your project name?[/]",
                console=console
            ).strip()
            
            if not name:
                console.print("[red]❌ Project name cannot be empty[/]")
                continue
                
            # Validate project name
            if not name.replace('_', '').replace('-', '').isalnum():
                console.print("[red]❌ Project name should only contain letters, numbers, hyphens, and underscores[/]")
                continue
                
            return name

    def get_project_path(self, name: str) -> str:
        """Get project path with existence check"""
        default_path = "."
        path = Prompt.ask(
            f"[bold bright_blue]📁 Where should we create '{name}'?[/]",
            default=default_path,
            console=console
        )
        
        project_path = os.path.join(path, name)
        
        if os.path.exists(project_path):
            console.print(f"\n[yellow]⚠️  Directory '{project_path}' already exists[/]")
            overwrite = Confirm.ask(
                "[yellow]Do you want to overwrite it?[/]",
                default=False
            )
            if not overwrite:
                console.print("[yellow]📦 Operation cancelled.[/]")
                sys.exit(0)
                
        return project_path

    def select_project_type(self) -> ProjectType:
        """Interactive project type selection with rich descriptions"""
        options = [
            {
                "value": ProjectType.API,
                "name": "Simple REST API",
                "description": "Basic CRUD operations with clean structure",
                "icon": "🚀",
                "use_cases": ["Quick prototypes", "Simple backends", "Learning FastAPI"]
            },
            {
                "value": ProjectType.CRUD,
                "name": "Full CRUD API",
                "description": "Complete database operations with advanced patterns",
                "icon": "🏗️",
                "use_cases": ["Production APIs", "Complex data models", "Enterprise apps"]
            },
            {
                "value": ProjectType.ML_API,
                "name": "Machine Learning API",
                "description": "ML model serving with prediction endpoints",
                "icon": "🤖",
                "use_cases": ["Model deployment", "AI services", "Data science"]
            },
            {
                "value": ProjectType.MICROSERVICE,
                "name": "Microservice",
                "description": "Service-oriented architecture ready",
                "icon": "⚡",
                "use_cases": ["Distributed systems", "Cloud native", "Scalable services"]
            }
        ]
        
        console.print("\n")
        console.print(Panel(
            "[bold bright_blue]🎯 Choose Your Project Type[/]",
            box=box.ROUNDED,
            style="bright_blue"
        ))
        
        # Create a table to display options beautifully
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        table.add_column("Option", style="bold", min_width=8)
        table.add_column("Type", style="bright_cyan", min_width=20)
        table.add_column("Description", style="white", min_width=35)
        table.add_column("Best For", style="dim", min_width=25)
        
        for i, option in enumerate(options, 1):
            use_cases_text = " • ".join(option["use_cases"])
            table.add_row(
                f"[bold bright_green]{i}[/]",
                f"{option['icon']} {option['name']}",
                option['description'],
                use_cases_text
            )
        
        console.print(table)
        console.print()
        
        while True:
            choice = IntPrompt.ask(
                "[bold bright_blue]Select project type[/]",
                default=1,
                choices=["1", "2", "3", "4"],
                console=console
            )
            
            if 1 <= choice <= len(options):
                selected = options[choice - 1]
                console.print(f"\n[bright_green]✅ Selected: {selected['icon']} {selected['name']}[/]")
                return selected["value"]

    def select_database(self) -> DatabaseType:
        """Interactive database selection"""
        options = [
            {
                "value": DatabaseType.SQLITE,
                "name": "SQLite",
                "description": "Lightweight file-based database",
                "icon": "📁",
                "pros": ["Zero setup", "Perfect for development", "Portable"],
                "best_for": "Development, Small apps"
            },
            {
                "value": DatabaseType.POSTGRESQL,
                "name": "PostgreSQL",
                "description": "Advanced relational database",
                "icon": "🐘",
                "pros": ["Full-featured", "Excellent performance", "ACID compliant"],
                "best_for": "Production, Complex queries"
            },
            {
                "value": DatabaseType.MYSQL,
                "name": "MySQL",
                "description": "Popular relational database",
                "icon": "🐬",
                "pros": ["Wide support", "Battle-tested", "Fast reads"],
                "best_for": "Web applications, High traffic"
            },
            {
                "value": DatabaseType.MONGODB,
                "name": "MongoDB",
                "description": "Document-based NoSQL database",
                "icon": "🍃",
                "pros": ["Flexible schema", "JSON-like documents", "Horizontal scaling"],
                "best_for": "Flexible data, Rapid development"
            }
        ]
        
        console.print(Panel(
            "[bold bright_blue]💾 Choose Your Database[/]",
            box=box.ROUNDED,
            style="bright_blue"
        ))
        
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        table.add_column("Option", style="bold", min_width=8)
        table.add_column("Database", style="bright_cyan", min_width=18)
        table.add_column("Description", style="white", min_width=30)
        table.add_column("Best For", style="dim", min_width=25)
        
        for i, option in enumerate(options, 1):
            table.add_row(
                f"[bold bright_green]{i}[/]",
                f"{option['icon']} {option['name']}",
                option['description'],
                option['best_for']
            )
        
        console.print(table)
        console.print()
        
        choice = IntPrompt.ask(
            "[bold bright_blue]Select database[/]",
            default=1,
            choices=["1", "2", "3", "4"],
            console=console
        )
        
        selected = options[choice - 1]
        console.print(f"\n[bright_green]✅ Selected: {selected['icon']} {selected['name']}[/]")
        return selected["value"]

    def select_authentication(self) -> AuthType:
        """Interactive authentication selection"""
        options = [
            {
                "value": AuthType.JWT,
                "name": "JWT (JSON Web Tokens)",
                "description": "Stateless token-based authentication",
                "icon": "🎫",
                "security": "High",
                "complexity": "Medium"
            },
            {
                "value": AuthType.OAUTH2,
                "name": "OAuth2 with Scopes",
                "description": "Enterprise-grade authorization",
                "icon": "🔐",
                "security": "Very High",
                "complexity": "High"
            },
            {
                "value": AuthType.API_KEY,
                "name": "API Key",
                "description": "Simple key-based authentication",
                "icon": "🗝️",
                "security": "Medium",
                "complexity": "Low"
            },
            {
                "value": AuthType.NONE,
                "name": "No Authentication",
                "description": "Open API (not recommended for production)",
                "icon": "🌐",
                "security": "None",
                "complexity": "None"
            }
        ]
        
        console.print(Panel(
            "[bold bright_blue]🔐 Choose Authentication Method[/]",
            box=box.ROUNDED,
            style="bright_blue"
        ))
        
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        table.add_column("Option", style="bold", min_width=8)
        table.add_column("Method", style="bright_cyan", min_width=25)
        table.add_column("Description", style="white", min_width=30)
        table.add_column("Security", style="yellow", min_width=12)
        
        for i, option in enumerate(options, 1):
            security_color = {
                "Very High": "bright_green",
                "High": "green", 
                "Medium": "yellow",
                "Low": "red",
                "None": "red"
            }.get(option["security"], "white")
            
            table.add_row(
                f"[bold bright_green]{i}[/]",
                f"{option['icon']} {option['name']}",
                option['description'],
                f"[{security_color}]{option['security']}[/]"
            )
        
        console.print(table)
        console.print()
        
        choice = IntPrompt.ask(
            "[bold bright_blue]Select authentication[/]",
            default=1,
            choices=["1", "2", "3", "4"],
            console=console
        )
        
        selected = options[choice - 1]
        console.print(f"\n[bright_green]✅ Selected: {selected['icon']} {selected['name']}[/]")
        return selected["value"]

    def configure_advanced_options(self) -> Dict[str, Any]:
        """Configure advanced options with beautiful prompts"""
        console.print(Panel(
            "[bold bright_blue]⚙️ Advanced Configuration[/]",
            box=box.ROUNDED,
            style="bright_blue"
        ))
        
        options = {}
        
        # Async/Sync
        options['is_async'] = Confirm.ask(
            "[cyan]🔄 Use async/await pattern?[/] [dim](Recommended for modern FastAPI)[/]",
            default=True
        )
        
        # Advanced features
        options['is_advanced'] = Confirm.ask(
            "[cyan]🚀 Include advanced features?[/] [dim](Middleware, background tasks, advanced routing)[/]",
            default=False
        )
        
        return options

    def configure_optional_features(self) -> Dict[str, Any]:
        """Configure optional features"""
        console.print(Panel(
            "[bold bright_blue]🎁 Optional Features[/]",
            box=box.ROUNDED,
            style="bright_blue"
        ))
        
        features = {}
        
        feature_options = [
            ("include_docker", "🐳 Docker configuration", "Containerize your application", True),
            ("include_tests", "🧪 Test setup", "Unit and integration tests with pytest", True),
            ("include_docs", "📚 Documentation", "Auto-generated API docs and guides", True),
            ("include_monitoring", "📊 Monitoring tools", "Prometheus metrics and health checks", False),
            ("include_celery", "⚡ Celery integration", "Background task processing", False)
        ]
        
        for key, title, description, default in feature_options:
            features[key] = Confirm.ask(
                f"[cyan]{title}[/] [dim]- {description}[/]",
                default=default
            )
        
        return features

    def show_configuration_summary(self, config: ProjectConfig):
        """Display beautiful configuration summary"""
        console.print()
        console.print(Panel(
            "[bold bright_green]📋 Configuration Summary[/]",
            box=box.DOUBLE,
            style="bright_green"
        ))
        
        # Create summary table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Setting", style="bold bright_blue", min_width=20)
        table.add_column("Value", style="bright_white", min_width=30)
        
        # Add configuration rows
        table.add_row("📝 Project Name", config.name)
        table.add_row("📁 Location", config.path)
        table.add_row("🎯 Type", config.project_type.value)
        table.add_row("💾 Database", config.database_type.value)
        table.add_row("🔐 Authentication", config.auth_type.value)
        table.add_row("🔄 Async/Await", "✅ Yes" if config.is_async else "❌ No")
        table.add_row("🚀 Advanced Features", "✅ Yes" if config.is_advanced else "❌ No")
        table.add_row("🐳 Docker", "✅ Yes" if config.include_docker else "❌ No")
        table.add_row("🧪 Tests", "✅ Yes" if config.include_tests else "❌ No")
        table.add_row("📚 Documentation", "✅ Yes" if config.include_docs else "❌ No")
        table.add_row("📊 Monitoring", "✅ Yes" if config.include_monitoring else "❌ No")
        table.add_row("⚡ Celery", "✅ Yes" if config.include_celery else "❌ No")
        table.add_row("🐍 Python Version", config.python_version)
        
        console.print(table)
        console.print()
        
        # Confirmation
        proceed = Confirm.ask(
            "[bold bright_blue]🚀 Ready to create your FastAPI project?[/]",
            default=True
        )
        
        if not proceed:
            console.print("[yellow]📦 Operation cancelled. Come back anytime![/]")
            sys.exit(0)

    def generate_with_progress(self, config: ProjectConfig):
        """Generate project with beautiful progress indicators"""
        console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            # Simulate project generation steps
            steps = [
                ("🏗️ Creating project structure", 0.2),
                ("📝 Generating configuration files", 0.15),
                ("💾 Setting up database models", 0.15),
                ("🔐 Configuring authentication", 0.15),
                ("🐳 Creating Docker setup", 0.1),
                ("🧪 Setting up tests", 0.1),
                ("📚 Generating documentation", 0.1),
                ("✨ Finalizing project", 0.05)
            ]
            
            total_task = progress.add_task("[cyan]Generating FastAPI project...", total=100)
            
            for step_name, duration in steps:
                step_task = progress.add_task(step_name, total=100)
                
                # Simulate work for each step
                for i in range(100):
                    time.sleep(duration / 100)  # Simulate work
                    progress.update(step_task, advance=1)
                    progress.update(total_task, advance=duration)
                
                progress.remove_task(step_task)
        
        # Generate the actual project (you'll replace the simulation above with this)
        generator = ProjectGenerator(config)
        generator.generate()

    def show_success_message(self, config: ProjectConfig):
        """Show beautiful success message with next steps"""
        console.print()
        
        # Success panel
        success_content = Align.center(
            f"[bold bright_green]🎉 Project '{config.name}' created successfully![/]\n"
            f"[bright_white]📁 Location: {config.path}[/]\n"
            f"[bright_white]🔧 Type: {config.project_type.value}[/]\n"
            f"[bright_white]💾 Database: {config.database_type.value}[/]\n"
            f"[bright_white]🔐 Auth: {config.auth_type.value}[/]"
        )
        
        console.print(Panel(
            success_content,
            title="[bold bright_green]✅ Success![/]",
            box=box.DOUBLE,
            style="bright_green",
            padding=(1, 2)
        ))
        
        # Next steps
        console.print(Panel(
            "[bold bright_blue]🚀 Next Steps[/]\n\n"
            f"[bright_white]1.[/] [cyan]cd {config.name}[/]\n"
            "[bright_white]2.[/] [cyan]pip install -r requirements.txt[/]\n"
            "[bright_white]3.[/] [cyan]uvicorn app.main:app --reload[/]\n"
            "[bright_white]4.[/] [cyan]Open http://localhost:8000[/]\n\n"
            "[dim]💡 Check out the README.md for detailed setup instructions![/]",
            title="[bold bright_blue]🎯 Get Started[/]",
            box=box.ROUNDED,
            style="bright_blue"
        ))
        
        console.print("\n[dim]Made with ❤️  by StartFast[/]")

    def interactive_config(self) -> ProjectConfig:
        """Full interactive configuration experience"""
        self.show_welcome_banner()
        
        # Get basic project info
        name = self.get_project_name()
        project_path = self.get_project_path(name)
        
        # Select project configuration
        project_type = self.select_project_type()
        database_type = self.select_database()
        auth_type = self.select_authentication()
        
        # Advanced options
        advanced_opts = self.configure_advanced_options()
        
        # Optional features
        optional_features = self.configure_optional_features()
        
        # Python version
        python_version = Prompt.ask(
            "[cyan]🐍 Python version[/]",
            default="3.11"
        )
        
        # Create configuration
        config = ProjectConfig(
            name=name,
            path=project_path,
            project_type=project_type,
            database_type=database_type,
            auth_type=auth_type,
            python_version=python_version,
            **advanced_opts,
            **optional_features
        )
        
        # Show summary and confirm
        self.show_configuration_summary(config)
        
        return config

    def main(self):
        """Main entry point with enhanced experience"""
        try:
            parser = self.create_argument_parser()
            args = parser.parse_args()

            # Configure logging level
            if args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)

            # Interactive mode by default (unless disabled or name provided)
            use_interactive = not args.no_interactive and not args.name
            
            if use_interactive:
                config = self.interactive_config()
            else:
                # Command line mode
                config = self.create_project_config_from_args(args)

            # Generate project with progress
            self.generate_with_progress(config)
            
            # Show success message
            self.show_success_message(config)

        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Operation cancelled by user. See you next time![/]")
            sys.exit(1)
        except Exception as e:
            console.print(f"\n[bold red]❌ Error generating project:[/] {e}")
            if args.verbose:
                console.print_exception()
            sys.exit(1)


def main():
    """Entry point"""
    cli = StartFastCLI()
    cli.main()


if __name__ == "__main__":
    main()