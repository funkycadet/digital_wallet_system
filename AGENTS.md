## Agent Instructions

### Build

This project uses Docker, so the build is handled by `docker-compose build`.

### Linting

Run `ruff check .` to lint the codebase.

### Testing

To run all tests for a service, navigate to the service's directory and run:
`python manage.py test`

To run a single test file:
`python manage.py test <app>.tests.<test_file>`

### Code Style

- **Formatting:** Follow PEP 8. Use `ruff format .` to format the code.
- **Imports:** Use `isort` to sort imports. Group imports into standard library, third-party, and local application imports.
- **Types:** Use type hints for all function signatures.
- **Naming:** Use `snake_case` for variables and functions. Use `PascalCase` for classes.
- **Error Handling:** Use `try...except` blocks for expected errors. Log exceptions instead of printing them.
- **Django:** Use Django's ORM and avoid raw SQL queries. Use Django's class-based views.
