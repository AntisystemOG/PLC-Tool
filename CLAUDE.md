# CLAUDE.md

Project-specific instructions for Claude Code.

## Project Overview

<!-- TODO: Describe what this project does -->

## Project Structure

```
.
├── src/          # Source code
├── tests/        # Test files (pytest)
├── pyproject.toml or setup.py
└── CLAUDE.md
```

<!-- Update the structure above to match your actual layout -->

## Commands & Workflows

```bash
# Install dependencies
uv sync            # or: pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .

# Format
black .
isort .
```

## Code Style & Conventions

- **Formatter**: black (line length 88), isort for imports
- **Linter**: ruff (or flake8)
- **Type hints**: use them for all function signatures
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE` for constants
- **Imports**: stdlib → third-party → local, separated by blank lines (enforced by isort)
- **Tests**: one test file per source module (`test_<module>.py`), use pytest fixtures
- Do not add docstrings or comments to code that was not changed

## Behavior Instructions

- **Ask before large changes**: confirm approach before refactoring, renaming across files, or making architectural decisions
- **Minimal changes**: only modify what is directly needed; avoid unrelated cleanup
- **No speculative features**: do not add error handling, fallbacks, or abstractions for hypothetical future needs
- **Prefer editing over creating**: update existing files rather than creating new ones
