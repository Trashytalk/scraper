# Developer Guide

This project follows a few simple conventions to keep the codebase consistent.

## Code Style

- Format all Python files with **black**.
- Lint the project with **ruff** and fix issues when possible.

```bash

pip install black ruff
black .
ruff .

```

Use `ruff --fix .` to automatically apply safe fixes.

## Running Tests

Install the development requirements and execute the test suite with pytest:

```bash

pip install -r requirements.txt
pytest

```

## Contribution Tips

- Keep functions small and focused.
- Document new modules and public functions with docstrings.
- Update or add tests when you change behaviour.
