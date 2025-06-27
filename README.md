<div align="center">

# 🚀 Fast Starter

### *The Ultimate FastAPI Project Generator*

*Create scalable, production-ready FastAPI projects in seconds*

[![PyPI version](https://badge.fury.io/py/faststarter.svg)](https://badge.fury.io/py/faststarter)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## ✨ Features

<table>
  <tr>
    <td>🚀 <strong>Project Types</strong></td>
    <td>API • CRUD • ML-API • Microservice</td>
  </tr>
  <tr>
    <td>💾 <strong>Databases</strong></td>
    <td>SQLite • PostgreSQL • MySQL • MongoDB • Redis</td>
  </tr>
  <tr>
    <td>🔐 <strong>Authentication</strong></td>
    <td>JWT • OAuth2 • API Key • None</td>
  </tr>
  <tr>
    <td>🐳 <strong>DevOps Ready</strong></td>
    <td>Docker • Docker Compose • Production configs</td>
  </tr>
  <tr>
    <td>📊 <strong>Observability</strong></td>
    <td>Monitoring • Logging • Health checks</td>
  </tr>
  <tr>
    <td>⚡ <strong>Performance</strong></td>
    <td>Async/Sync • Background tasks • Caching</td>
  </tr>
  <tr>
    <td>🧪 <strong>Quality</strong></td>
    <td>Testing suite • Code formatting • Documentation</td>
  </tr>
</table>

## 📦 Installation

### 🎯 Quick Install

```bash
pip install faststarter
```

### 🛠️ Development Install

```bash
git clone https://github.com/Incognitol07/faststarter.git
cd faststarter
pip install -e .
```

---

## 🚀 Quick Start

### ⚡ Generate Your First Project

```bash
faststarter my-awesome-api
```

### 🎨 Custom Configuration

```bash
faststarter my-api --type crud --database postgresql --auth jwt --advanced
```

---

## 🎯 Usage

### 📋 Command Syntax

```bash
faststarter PROJECT_NAME [OPTIONS]
```

### ⚙️ Configuration Options

| Option | Description | Values |
|--------|-------------|--------|
| `--path` | Project directory | Directory path |
| `--type` | Project architecture | `api`, `crud`, `ml-api`, `microservice` |
| `--database` | Database backend | `sqlite`, `postgresql`, `mysql`, `mongodb`, `redis` |
| `--auth` | Authentication method | `none`, `jwt`, `oauth2`, `api-key` |
| `--sync` | Synchronous implementation | Flag |
| `--advanced` | Advanced features | Flag |
| `--no-docker` | Skip Docker setup | Flag |
| `--no-tests` | Skip test configuration | Flag |
| `--no-docs` | Skip documentation | Flag |
| `--monitoring` | Include observability | Flag |
| `--celery` | Background task support | Flag |
| `--python-version` | Python version | Version string (default: 3.11) |
| `--force` | Overwrite existing files | Flag |

### 🌟 Usage Examples

<details>
<summary><strong>🔧 Simple API with SQLite</strong></summary>

```bash
faststarter simple-api
```
</details>

<details>
<summary><strong>🗄️ CRUD API with PostgreSQL and JWT</strong></summary>

```bash
faststarter crud-api --type crud --database postgresql --auth jwt
```
</details>

<details>
<summary><strong>🤖 ML API with Advanced Features</strong></summary>

```bash
faststarter ml-service --type ml-api --advanced --monitoring
```
</details>

<details>
<summary><strong>🏗️ Microservice with MongoDB and Celery</strong></summary>

```bash
faststarter micro-service --type microservice --database mongodb --celery
```
</details>

---

## 🏗️ Project Architecture

Generated projects follow a **clean, scalable structure**:

```
📁 my-project/
├── 📂 app/
│   ├── 🐍 __init__.py
│   ├── 🚀 main.py                 # FastAPI app entry point
│   ├── 📂 core/
│   │   ├── ⚙️ config.py          # Configuration management
│   │   └── 🔐 security.py        # Authentication & security
│   ├── 📂 api/
│   │   └── 📂 v1/                # API version 1
│   ├── 📂 models/                # Database models
│   ├── 📂 schemas/               # Pydantic schemas
│   ├── 📂 services/              # Business logic
│   └── 📂 utils/                 # Helper functions
├── 📂 tests/                     # Test suite
├── 📂 docs/                      # Documentation
├── 📄 requirements.txt           # Dependencies
├── 🐳 Dockerfile                # Container configuration
├── 🐙 docker-compose.yml        # Multi-service setup
└── 📖 README.md                 # Project documentation
```

---

## 🛠️ Development

### 🚧 Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Incognitol07/faststarter.git
cd faststarter

# Install in development mode
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install
```

### 🧪 Running Tests

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov              # With coverage report
```

### 🎨 Code Quality

```bash
black .                   # Format code
isort .                   # Sort imports
flake8 .                  # Lint code
mypy .                    # Type checking
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### 🔄 Contribution Workflow

1. **🍴 Fork** the repository
2. **🌿 Create** your feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **💾 Commit** your changes
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **📤 Push** to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. **🔀 Open** a Pull Request

### 📝 Contribution Guidelines

- Write clear, concise commit messages
- Add tests for new features
- Update documentation as needed
- Follow the existing code style
- Ensure all tests pass

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🗺️ Roadmap

### 🔮 Upcoming Features

- [ ] 🌐 **Web UI** for project generation
- [ ] 📊 **More database adapters** (ClickHouse, TimescaleDB)
- [ ] 🎨 **Custom template support**
- [ ] 🔌 **Plugin system** for extensibility
- [ ] 💻 **IDE integrations** (VS Code, PyCharm)
- [ ] ☁️ **Cloud deployment templates**
- [ ] 📱 **Mobile-first API templates**

---

## 📞 Support & Community

<div align="center">

### � Get Help & Connect

[![Email](https://img.shields.io/badge/Email-ab.adelodun%40gmail.com-blue?style=for-the-badge&logo=gmail)](mailto:ab.adelodun@gmail.com)
[![GitHub Issues](https://img.shields.io/badge/Issues-Report%20Bug-red?style=for-the-badge&logo=github)](https://github.com/Incognitol07/faststarter/issues)
[![GitHub Discussions](https://img.shields.io/badge/Discussions-Join%20Community-green?style=for-the-badge&logo=github)](https://github.com/Incognitol07/faststarter/discussions)

### 🌟 Show Your Support

If Fast Starter helped you build amazing projects, consider giving it a ⭐!

[![Star on GitHub](https://img.shields.io/github/stars/Incognitol07/faststarter?style=social)](https://github.com/Incognitol07/faststarter)

</div>

---

<div align="center">

**Made with ❤️ by developers, for developers**

*Happy coding! 🚀*

</div>
