# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`comments-spa` is a Django REST Framework backend for a comments single-page application. It uses PostgreSQL, JWT authentication, CAPTCHA, and HTML sanitization via bleach.

## Setup

```bash
poetry install
```

Requires a PostgreSQL database. Copy `local_settings.py` (gitignored) for local DB credentials.

## Common Commands

```bash
# Run development server
poetry run python manage.py runserver

# Apply migrations
poetry run python manage.py migrate

# Create migrations
poetry run python manage.py makemigrations

# Run tests
poetry run pytest

# Run a single test
poetry run pytest path/to/test_file.py::TestClass::test_method

# Lint
poetry run ruff check .

# Format / auto-fix
poetry run ruff check --fix .
```

## Key Dependencies

| Package | Purpose |
|---|---|
| `djangorestframework` | REST API layer |
| `djangorestframework-simplejwt` | JWT auth (access + refresh tokens) |
| `django-cors-headers` | CORS for SPA frontend |
| `django-simple-captcha` | CAPTCHA on comment submission |
| `bleach` | Sanitize HTML in comment content |
| `psycopg2` | PostgreSQL adapter |
| `pillow` | Image handling (avatars/captcha) |

## Linting

Ruff is configured with `E`, `F`, `I` (isort), and `DJ` (Django) rule sets at line length 88. Run `ruff check .` before committing.

## Testing

`pytest-django` is used. Tests require a `pytest.ini` or `pyproject.toml` `[tool.pytest.ini_options]` block pointing at the Django settings module (`DJANGO_SETTINGS_MODULE`).