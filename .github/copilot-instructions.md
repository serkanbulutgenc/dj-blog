# Repository guidance

## Project structure

- This is a Django 6 blog project using Python 3.14, `uv`, PostgreSQL, and a local Docker Compose stack. The project dependencies and pytest, Ruff, mypy, and djLint settings live in `pyproject.toml`.
- `config/settings/base.py` defines shared Django settings; `local.py`, `production.py`, and `test.py` layer environment-specific settings over it. `config/urls.py` joins the rendered Django pages, user/account routes, and `/api/v1/`.
- Blog domain models are in `apps/blog/models.py`. API request/response schemas are in `apps/blog/api/schemas.py`; resource routers are in `apps/blog/api/routers/` and are gathered by `apps/blog/api/__init__.py`, then mounted by `config/api.py`.
- The custom `apps.users.models.User` deliberately has no `first_name` or `last_name` fields; those profile values live on `Profile`. Signup changes involving those values may also need corresponding updates to the user forms.
- Django migrations are kept with their owning apps. CI checks for ungenerated model changes before applying migrations.

## API and test conventions

- Keep API route registration centralized in `config/api.py`. Use the existing Django Ninja router and Pydantic/Django `ModelSchema` patterns in the blog API; list endpoints use `FilterSchema` and pagination.
- The README describes posts API access as bearer access-token authentication plus the user's blog permissions. Swagger documentation access is separately staff-gated; an API `401` means authentication failed and `403` means the user lacks permission.
- Tests use pytest-django with `config.settings.test` (configured in `pyproject.toml`), and factories/fixtures are provided under each app's test modules and `conftest.py`. Tests may be named `tests.py` or `test_*.py`.

## Commands

Run commands from the repository root. The project pins Python 3.14 in `.python-version` and `pyproject.toml`.

```sh
# Install/synchronize project and development dependencies
uv sync --all-groups

# Build and start the local Docker Compose stack
just build
just up

# Run the full test suite (using the local Docker Compose service)
just pytest

# Run one test (locally, or replace `uv run pytest` with `just pytest` to use Docker)
uv run pytest apps/users/tests/test_models.py::test_user_get_absolute_url

# Run the repository's configured hooks
uv run pre-commit run --all-files

# Run Ruff lint/format checks on one file
uv run pre-commit run ruff-check --files apps/blog/api/routers/posts.py
uv run pre-commit run ruff-format --files apps/blog/api/routers/posts.py

# Run the documented type check
uv run mypy django_blog

# Check for model changes without migrations, as CI does
docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations --check

# Build the Sphinx documentation
uv run make -C docs html
```

`just down` stops the local stack. The CI workflow runs pre-commit, checks migrations, applies migrations, and runs pytest through Docker Compose.
