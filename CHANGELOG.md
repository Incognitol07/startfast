# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project structure for PyPI package
- CLI interface with `fast-starter` command
- Support for multiple project types (API, CRUD, ML-API, Microservice)
- Multiple database support (SQLite, PostgreSQL, MySQL, MongoDB, Redis)
- Authentication options (JWT, OAuth2, API Key, None)
- Docker configuration generation
- Test suite generation
- Documentation generation
- Monitoring and Celery support
- Template system with Jinja2

### Changed

- Restructured project for proper PyPI packaging
- Moved from simple script to full package structure
- Updated imports and module organization

### Fixed

- Import paths for proper package structure

## [0.1.0] - 2025-06-17

### Added

- Initial release structure
- Basic FastAPI project generation
- Core generator classes
