# Development Guide

This guide provides instructions for setting up the development environment for the Story Protocol Python SDK.

## Prerequisites

- Python 3.10 or higher
- Git
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

## Installing uv

uv is a fast Python package installer and resolver written in Rust. It's a drop-in replacement for pip and pip-tools.

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Alternative: Install via pip
```bash
pip install uv
```

## Setting Up the Development Environment

### 1. Clone the repository
```bash
git clone https://github.com/storyprotocol/python-sdk.git
cd python-sdk
```

### 2. Create and activate a virtual environment with uv
```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install dependencies with uv
```bash
# Install the package in editable mode with all dependencies
uv pip install -e .

# Install additional development dependencies
uv pip install pytest pytest-cov black isort ruff pre-commit python-dotenv
```

### 4. Set up pre-commit hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files to ensure everything is set up correctly
pre-commit run --all-files
```

## Development Workflow

### Running Tests

```bash
# Run all integration tests (default)
pytest

# Run unit tests with coverage
coverage run -m pytest tests/unit -v -ra -q
coverage report

# Run specific test file
pytest tests/integration/test_integration_ip_asset.py -v

# Run tests with specific markers
pytest -m integration  # Run only integration tests
pytest -m unit        # Run only unit tests
```

### Code Formatting and Linting

The project uses several tools to maintain code quality:

1. **Black** - Code formatter
   ```bash
   black .
   ```

2. **isort** - Import sorter
   ```bash
   isort . --profile black
   ```

3. **Ruff** - Fast Python linter
   ```bash
   ruff check . --fix
   ```

All these tools are automatically run as pre-commit hooks when you commit code.

### Type Checking

```bash
mypy .
```

### Manual Pre-commit Checks

To manually run all pre-commit checks:
```bash
pre-commit run --all-files
```

To run a specific hook:
```bash
pre-commit run black --all-files
pre-commit run ruff --all-files
```

## Pre-commit Hooks Overview

The project uses the following pre-commit hooks:

| Hook | Purpose |
|------|---------|
| `trailing-whitespace` | Removes trailing whitespace |
| `end-of-file-fixer` | Ensures files end with a newline |
| `check-yaml` | Validates YAML syntax |
| `check-added-large-files` | Prevents large files from being committed |
| `check-json` | Validates JSON syntax |
| `check-merge-conflict` | Checks for merge conflict markers |
| `check-toml` | Validates TOML syntax |
| `debug-statements` | Checks for debugger imports |
| `mixed-line-ending` | Normalizes line endings |
| `black` | Formats Python code |
| `isort` | Sorts Python imports |
| `ruff` | Lints Python code and auto-fixes issues |

## Updating Dependencies with uv

### Add a new dependency
```bash
# Add to setup.py's install_requires, then:
uv pip install -e .
```

### Upgrade dependencies
```bash
# Upgrade specific package
uv pip install --upgrade package-name

# Upgrade all packages
uv pip install --upgrade -e .
```

### Speed Comparison

uv is significantly faster than pip:
- **Installation**: 10-100x faster than pip
- **Resolution**: More efficient dependency resolver
- **Caching**: Better cache utilization

## Environment Variables

Create a `.env` file in the project root for local development:
```env
WALLET_PRIVATE_KEY=your_private_key_here
RPC_PROVIDER_URL=https://aeneid.storyrpc.io
```

## Troubleshooting

### Pre-commit hooks failing

1. Ensure all tools are installed:
   ```bash
   uv pip install black isort ruff pre-commit
   ```

2. Update pre-commit hooks:
   ```bash
   pre-commit autoupdate
   ```

3. Clear pre-commit cache:
   ```bash
   pre-commit clean
   ```

### Import errors

1. Ensure you're in the virtual environment:
   ```bash
   which python  # Should point to .venv/bin/python
   ```

2. Reinstall in editable mode:
   ```bash
   uv pip install -e .
   ```

### uv installation issues

If uv is not working properly:
1. Try installing via pip: `pip install uv`
2. Ensure it's in your PATH: `which uv`
3. On Windows, restart your terminal after installation

## Contributing

Before submitting a pull request:

1. Ensure all tests pass: `pytest`
2. Run pre-commit checks: `pre-commit run --all-files`
3. Update tests if adding new functionality
4. Follow the existing code style and patterns

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.
