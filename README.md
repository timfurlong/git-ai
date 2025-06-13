# Git AI

A Python project using uv for dependency management.

## Setup

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

uv pip install -r requirements.txt
```

## Development

- Use `ruff` for linting
- Use `black` for code formatting
- Use `pytest` for testing

## Project Structure

```
.
├── pyproject.toml    # Project configuration
├── requirements.txt  # Project dependencies
└── src/             # Source code directory
``` 