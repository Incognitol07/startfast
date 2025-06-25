# Fast Starter

A comprehensive FastAPI project generator that creates scalable, modular FastAPI projects with various configurations.

## Features

- 🚀 **Multiple Project Types**: API, CRUD, ML-API, Microservice
- 💾 **Database Support**: SQLite, PostgreSQL, MySQL, MongoDB, Redis
- 🔐 **Authentication**: JWT, OAuth2, API Key, or None
- 🐳 **Docker Ready**: Optional Docker configuration
- 📊 **Monitoring**: Optional observability tools
- ⚡ **Async/Sync**: Support for both async and sync implementations
- 🧪 **Testing**: Built-in test setup
- 📚 **Documentation**: Automatic documentation generation
- 🔄 **Background Tasks**: Optional Celery integration

## Installation

### From PyPI

```bash
pip install fast-starter
```

### From Source

```bash
git clone https://github.com/Incognitol07/fast-starter.git
cd fast-starter
pip install -e .
```

## Quick Start

Generate a new FastAPI project:

```bash
fast-starter my-awesome-api
```

With custom configuration:

```bash
fast-starter my-api --type crud --database postgresql --auth jwt --advanced
```

## Usage

### Basic Usage

```bash
fast-starter PROJECT_NAME [OPTIONS]
```

### Options

- `--path`: Directory where project will be created (default: current directory)
- `--type`: Project type (`api`, `crud`, `ml-api`, `microservice`)
- `--database`: Database type (`sqlite`, `postgresql`, `mysql`, `mongodb`, `redis`)
- `--auth`: Authentication method (`none`, `jwt`, `oauth2`, `api-key`)
- `--sync`: Generate synchronous version (default is async)
- `--advanced`: Include advanced features and configurations
- `--no-docker`: Skip Docker configuration
- `--no-tests`: Skip test setup
- `--no-docs`: Skip documentation setup
- `--monitoring`: Include monitoring and observability tools
- `--celery`: Include Celery for background tasks
- `--python-version`: Python version for the project (default: 3.11)
- `--force`: Overwrite existing directory without confirmation

### Examples

```bash
# Simple API with SQLite
fast-starter simple-api

# CRUD API with PostgreSQL and JWT auth
fast-starter crud-api --type crud --database postgresql --auth jwt

# ML API with advanced features
fast-starter ml-service --type ml-api --advanced --monitoring

# Microservice with MongoDB and Celery
fast-starter micro-service --type microservice --database mongodb --celery
```

## Project Structure

Generated projects follow a clean, scalable structure:

```plaintext
my-project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── api/
│   │   └── v1/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── tests/
├── docs/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/Incognitol07/fast-starter.git
cd fast-starter
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
flake8 .
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Web UI for project generation
- [ ] More database adapters
- [ ] Custom template support
- [ ] Plugin system
- [ ] Integration with popular IDEs

## Support

- 📧 Email: <ab.adelodun@gmail.com>
- 🐛 Issues: [GitHub Issues](https://github.com/Incognitol07/fast-starter/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Incognitol07/fast-starter/discussions)
