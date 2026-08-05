# Kishai - LLM Deployment Platform
# Development automation with just (https://just.systems)

# Show available commands
default:
    @just --list

# Setup local development environment
setup:
    @echo "🚀 Setting up development environment..."
    uv venv
    uv pip install -e ".[dev]"
    @echo "✅ Development environment ready!"
    @echo "💡 Activate with: source .venv/bin/activate"

# Install dependencies
install:
    uv pip install -e ".[dev]"

# Sync dependencies (update to match pyproject.toml)
sync:
    uv pip sync

# Run the backend development server
dev:
    @echo "🚀 Starting development server..."
    cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run the backend with custom host and port
serve host="0.0.0.0" port="8000":
    cd backend && uvicorn app.main:app --reload --host {{host}} --port {{port}}

# Format code with ruff
fmt:
    @echo "🎨 Formatting code..."
    ruff format .
    ruff check --fix .

# Lint code with ruff
lint:
    @echo "🔍 Linting code..."
    ruff check .

# Type check with mypy
typecheck:
    @echo "🔎 Type checking..."
    mypy backend/app

# Run all checks (lint, format check, type check)
check:
    @echo "🔍 Running all checks..."
    ruff check .
    ruff format --check .
    mypy backend/app

# Run tests
test:
    @echo "🧪 Running tests..."
    pytest

# Run tests with coverage
test-cov:
    @echo "🧪 Running tests with coverage..."
    pytest --cov=backend/app --cov-report=term-missing --cov-report=html

# Run tests in watch mode
test-watch:
    @echo "👀 Running tests in watch mode..."
    pytest-watch

# Clean up generated files
clean:
    @echo "🧹 Cleaning up..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    rm -rf htmlcov/ .coverage dist/ build/
    @echo "✅ Cleanup complete!"

# Clean everything including venv
clean-all: clean
    @echo "🧹 Cleaning virtual environment..."
    rm -rf .venv
    @echo "✅ Deep cleanup complete!"

# Create a new database migration (requires alembic setup)
migrate message:
    @echo "📝 Creating migration: {{message}}"
    cd backend && alembic revision --autogenerate -m "{{message}}"

# Apply database migrations
migrate-up:
    @echo "⬆️  Applying migrations..."
    cd backend && alembic upgrade head

# Rollback last migration
migrate-down:
    @echo "⬇️  Rolling back migration..."
    cd backend && alembic downgrade -1

# Show migration history
migrate-history:
    cd backend && alembic history

# Create .env file from example
env:
    @if [ ! -f .env ]; then \
        cp .env.example .env; \
        echo "✅ Created .env file from .env.example"; \
        echo "⚠️  Please edit .env and set your configuration"; \
    else \
        echo "⚠️  .env file already exists"; \
    fi

# Generate a secure SECRET_KEY
secret:
    @python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Initialize database
db-init:
    @echo "🗄️  Initializing database..."
    @python3 -c "import asyncio; from backend.app.database import init_db; asyncio.run(init_db())"
    @echo "✅ Database initialized!"

# Reset database (WARNING: deletes all data)
db-reset:
    @echo "⚠️  WARNING: This will delete all data!"
    @read -p "Are you sure? [y/N] " -n 1 -r; \
    echo; \
    if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
        rm -f bku.db; \
        echo "🗄️  Database deleted. Run 'just db-init' to recreate."; \
    fi

# Install pre-commit hooks
hooks:
    @echo "🪝 Installing pre-commit hooks..."
    pre-commit install
    @echo "✅ Pre-commit hooks installed!"

# Run pre-commit on all files
hooks-run:
    pre-commit run --all-files

# Update dependencies to latest versions
upgrade:
    @echo "⬆️  Upgrading dependencies..."
    uv pip install --upgrade -e ".[dev]"

# Show project info
info:
    @echo "📦 Kishai - LLM Deployment Platform"
    @echo "=================================="
    @echo "Python: $(python3 --version)"
    @echo "UV: $(uv --version)"
    @echo "Just: $(just --version)"
    @echo ""
    @if [ -d .venv ]; then \
        echo "✅ Virtual environment: .venv (active)"; \
    else \
        echo "❌ Virtual environment: not found"; \
    fi

# Pull an Ollama model (for local testing)
ollama-pull model="llama2":
    @echo "📥 Pulling Ollama model: {{model}}"
    ollama pull {{model}}

# List Ollama models
ollama-list:
    ollama list

# Start Ollama service (if not running)
ollama-start:
    @if pgrep -x "ollama" > /dev/null; then \
        echo "✅ Ollama is already running"; \
    else \
        echo "🚀 Starting Ollama..."; \
        ollama serve & \
    fi

# Check if required tools are installed
check-tools:
    @echo "🔧 Checking required tools..."
    @command -v python3 >/dev/null 2>&1 || { echo "❌ python3 not found"; exit 1; }
    @command -v uv >/dev/null 2>&1 || { echo "❌ uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
    @command -v just >/dev/null 2>&1 || { echo "❌ just not found. Install: cargo install just"; exit 1; }
    @echo "✅ All required tools are installed!"

# Verify complete development setup
verify:
    @echo "🔍 Verifying development environment..."
    @python3 scripts/verify_setup.py

# Open API documentation in browser
docs:
    @echo "📚 Opening API documentation..."
    @(sleep 2 && xdg-open http://localhost:8000/docs 2>/dev/null || open http://localhost:8000/docs 2>/dev/null) &

# Quick start - setup and run
start: setup env
    @echo ""
    @echo "🎉 Setup complete! Starting development server..."
    @echo "📝 Don't forget to configure your .env file"
    @echo ""
    @just dev


# --- evals -------------------------------------------------------------------

# Run the eval gate against committed recordings (deterministic, no model needed)
eval:
    python -m evals.harness --mode replay

# Re-record model outputs, then review the diff before committing
eval-record model="qwen3.5:9b":
    python -m evals.harness --mode record --model {{model}}

# Run against the live model — catches drift that replay cannot see
eval-live model="qwen3.5:9b":
    python -m evals.harness --mode live --model {{model}}

# Accept the current scores as the new regression baseline (review the diff!)
eval-baseline:
    python -m evals.harness --mode replay --update-baseline
