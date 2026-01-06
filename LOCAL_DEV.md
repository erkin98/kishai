# Local Development Setup

This guide will help you set up the Kishai LLM Platform for local development using modern Python tools.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Tools

1. **Python 3.11+**
   ```bash
   python3 --version  # Should be 3.11 or higher
   ```

2. **uv** (Fast Python package installer)
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Verify installation
   uv --version
   ```

3. **just** (Command runner)
   ```bash
   # Install just (multiple options)
   
   # Using cargo (Rust)
   cargo install just
   
   # Using Homebrew (macOS/Linux)
   brew install just
   
   # Using pacman (Arch Linux)
   sudo pacman -S just
   
   # Verify installation
   just --version
   ```

4. **Ollama** (Optional, for local LLM inference)
   ```bash
   # Download from https://ollama.ai/download
   # Or use:
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Verify installation
   ollama --version
   ```

## Quick Start

The fastest way to get started:

```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd kishai

# Check if all tools are installed
just check-tools

# Setup everything and start
just start
```

This will:
1. Create a virtual environment
2. Install all dependencies
3. Create a `.env` file from `.env.example`
4. Start the development server

## Step-by-Step Setup

If you prefer to do it step by step:

### 1. Setup Development Environment

```bash
# Create virtual environment and install dependencies
just setup

# Activate the virtual environment
source .venv/bin/activate

# Or on Windows
# .venv\Scripts\activate
```

### 2. Configure Environment

```bash
# Create .env file
just env

# Generate a secure SECRET_KEY
just secret

# Edit .env and update the SECRET_KEY and other settings
nano .env  # or use your favorite editor
```

### 3. Initialize Database

```bash
# Create database tables
just db-init
```

### 4. Start Development Server

```bash
# Start the backend server
just dev

# Or with custom host/port
just serve 127.0.0.1 8080
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Available Commands

Run `just` to see all available commands:

```bash
just  # Shows all commands
```

### Development Commands

```bash
just dev              # Start development server
just serve HOST PORT  # Start with custom host/port
just test             # Run tests
just test-cov         # Run tests with coverage
just test-watch       # Run tests in watch mode
```

### Code Quality

```bash
just fmt              # Format code with ruff
just lint             # Lint code with ruff
just typecheck        # Type check with mypy
just check            # Run all checks (lint + format + typecheck)
```

### Database Management

```bash
just db-init          # Initialize database
just db-reset         # Reset database (WARNING: deletes data)
just migrate MESSAGE  # Create new migration
just migrate-up       # Apply migrations
just migrate-down     # Rollback last migration
just migrate-history  # Show migration history
```

### Ollama Management

```bash
just ollama-start           # Start Ollama service
just ollama-pull MODEL      # Pull a model (e.g., just ollama-pull llama2)
just ollama-list            # List installed models
```

### Utility Commands

```bash
just clean            # Clean up generated files
just clean-all        # Clean everything including venv
just upgrade          # Upgrade dependencies
just info             # Show project info
just secret           # Generate a secure SECRET_KEY
just hooks            # Install pre-commit hooks
just hooks-run        # Run pre-commit on all files
```

## Project Structure

```
kishai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   ├── api/              # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── inference.py
│   │   │   ├── deployments.py
│   │   │   ├── models.py
│   │   │   └── monitoring.py
│   │   └── auth/             # Authentication
│   │       ├── schemas.py
│   │       └── security.py
│   └── Dockerfile
├── pyproject.toml            # Project dependencies (uv)
├── justfile                  # Task automation (just)
├── .env.example              # Environment template
├── .env                      # Your environment (git-ignored)
└── README.md
```

## Development Workflow

### 1. Make Changes

Edit files in `backend/app/`

### 2. Format and Lint

```bash
# Format your code
just fmt

# Or run all checks
just check
```

### 3. Test Your Changes

```bash
# Run tests
just test

# Or with coverage
just test-cov
```

### 4. Run the Server

The development server auto-reloads when you save files:

```bash
just dev
```

## Working with Ollama

### Local Ollama Setup

1. **Start Ollama service**:
   ```bash
   just ollama-start
   ```

2. **Pull a model**:
   ```bash
   just ollama-pull llama2
   # or
   just ollama-pull mistral
   ```

3. **List installed models**:
   ```bash
   just ollama-list
   ```

4. **Update your deployment** to point to `http://localhost:11434`

## Testing the API

### Using the Interactive Docs

Open http://localhost:8000/docs in your browser for an interactive API explorer.

### Using curl

```bash
# Register a user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123",
    "full_name": "Test User"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'

# Health check
curl http://localhost:8000/health
```

### Using the Python client (app.py)

```bash
# Edit app.py with your model and prompt
python app.py
```

## Troubleshooting

### Virtual environment not activating

```bash
# Recreate it
just clean-all
just setup
source .venv/bin/activate
```

### Database errors

```bash
# Reset the database
just db-reset
just db-init
```

### Port already in use

```bash
# Use a different port
just serve 0.0.0.0 8080
```

### Ollama connection fails

```bash
# Check if Ollama is running
ollama list

# Start Ollama
just ollama-start

# Check the DEFAULT_OLLAMA_HOST in .env
```

### Import errors

```bash
# Reinstall dependencies
just install

# Or sync dependencies
just sync
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Ruff
- Even Better TOML
- SQLite Viewer

Add to `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  }
}
```

### PyCharm

1. Open the project
2. Set interpreter to `.venv/bin/python`
3. Enable Ruff in Settings → Tools → Ruff

## Contributing

When contributing:

1. Install pre-commit hooks: `just hooks`
2. Format your code: `just fmt`
3. Run checks: `just check`
4. Run tests: `just test`
5. Commit your changes

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [just Documentation](https://just.systems/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

## Need Help?

- Check the main [README.md](./README.md)
- Review [API_EXAMPLES.md](./API_EXAMPLES.md)
- Open an issue on GitHub
- Check the API docs at http://localhost:8000/docs

