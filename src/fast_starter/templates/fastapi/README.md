"""
{{ project_name }}
{% for char in project_name %}={% endfor %}

A FastAPI project generated with Fast Starter.

## Features

- FastAPI {{ project_type }} application
- {{ database_type|title }} database
- {{ auth_type|title }} authentication
{% if is_async -%}
- Asynchronous operations
{% endif -%}
{% if include_docker -%}
- Docker support
{% endif -%}
{% if include_tests -%}
- Test suite included
{% endif -%}
{% if include_docs -%}
- Documentation setup
{% endif -%}

## Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:

   ```bash
   uvicorn app.main:app --reload
   ```

## Development

The application will be available at: <http://localhost:8000>

API documentation: <http://localhost:8000/docs>
