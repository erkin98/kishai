# Getting Started with Kishai

Welcome to Kishai! This guide will help you get up and running quickly.

## Prerequisites

You need to install these tools first:

### 1. Python 3.11+
```bash
python3 --version  # Should be 3.11 or higher
```

If not installed:
- **Ubuntu/Debian**: `sudo apt install python3.11`
- **macOS**: `brew install python@3.11`
- **Windows**: Download from [python.org](https://python.org)

### 2. uv (Fast Python Package Manager)
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your shell or source your profile
source ~/.bashrc  # or ~/.zshrc

# Verify
uv --version
```

### 3. just (Command Runner)
```bash
# Option 1: Using cargo (if you have Rust)
cargo install just

# Option 2: Using Homebrew (macOS/Linux)
brew install just

# Option 3: Using package manager
# Ubuntu/Debian (requires adding PPA)
# See: https://just.systems/man/en/chapter_4.html

# Verify
just --version
```

### 4. Ollama (Optional, for local LLM inference)
```bash
# Download and install from https://ollama.ai/download
# Or on Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Verify
ollama --version
```

## Quick Setup

Once you have the prerequisites:

### Option 1: Automated Setup (Recommended)
```bash
# Run the setup script
./SETUP.sh

# Follow the prompts
```

### Option 2: Manual Setup
```bash
# 1. Check that tools are installed
just check-tools

# 2. Create virtual environment and install dependencies
just setup

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Create environment file
just env

# 5. Generate a secure SECRET_KEY
just secret

# 6. Edit .env and paste your SECRET_KEY
nano .env  # or your favorite editor

# 7. Initialize database
just db-init

# 8. Start the development server
just dev
```

## Verify Your Setup

At any time, you can verify your setup:

```bash
python3 scripts/verify_setup.py
# or
just verify
```

## First Steps

### 1. Start the Server
```bash
# Activate virtual environment (if not already)
source .venv/bin/activate

# Start development server
just dev
```

The server will start at http://localhost:8000

### 2. Explore the API

Open your browser and visit:
- **API Root**: http://localhost:8000/
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 3. Pull an Ollama Model (Optional)

If you want to test LLM inference locally:

```bash
# In a new terminal
just ollama-start
just ollama-pull llama2

# List available models
just ollama-list
```

### 4. Create a User

Use the interactive docs at http://localhost:8000/docs:

1. Find the `POST /api/v1/auth/register` endpoint
2. Click "Try it out"
3. Fill in the request body:
   ```json
   {
     "email": "user@example.com",
     "username": "testuser",
     "password": "securepassword123",
     "full_name": "Test User"
   }
   ```
4. Click "Execute"

### 5. Login and Get a Token

1. Find the `POST /api/v1/auth/login` endpoint
2. Fill in your credentials
3. Copy the returned `access_token`

### 6. Test the API

Use the token to make authenticated requests:

1. Click the "Authorize" button at the top of the docs
2. Enter: `Bearer YOUR_TOKEN_HERE`
3. Now you can test protected endpoints!

## Common Tasks

### Run Tests
```bash
just test

# With coverage
just test-cov

# Watch mode (auto-rerun on changes)
just test-watch
```

### Format Code
```bash
just fmt
```

### Lint Code
```bash
just lint
```

### Run All Checks
```bash
just check
```

### Clean Up
```bash
# Clean generated files
just clean

# Clean everything including venv
just clean-all
```

### Database Management
```bash
# Initialize database
just db-init

# Reset database (WARNING: deletes all data)
just db-reset

# Create migration
just migrate "description of changes"

# Apply migrations
just migrate-up

# Rollback migration
just migrate-down
```

### View Available Commands
```bash
just  # Shows all available commands
```

## Project Structure

```
kishai/
├── backend/app/         # Main application code
│   ├── api/            # API endpoints
│   ├── auth/           # Authentication
│   ├── models/         # Database models
│   ├── services/       # Business logic
│   ├── middleware/     # Custom middleware
│   └── utils/          # Utilities
├── tests/              # Test suite
├── scripts/            # Utility scripts
├── .env                # Your configuration (create from .env.example)
└── pyproject.toml      # Project dependencies
```

## Development Workflow

1. **Activate virtual environment**
   ```bash
   source .venv/bin/activate
   ```

2. **Make changes** to code in `backend/app/`

3. **Format and check**
   ```bash
   just fmt
   just check
   ```

4. **Run tests**
   ```bash
   just test
   ```

5. **Test manually** via the API docs at http://localhost:8000/docs

6. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: your change description"
   ```

## Troubleshooting

### "just: command not found"
- Make sure just is installed: `cargo install just` or `brew install just`
- Restart your terminal

### "uv: command not found"
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Source your shell profile: `source ~/.bashrc` or `source ~/.zshrc`

### Virtual environment issues
```bash
just clean-all
just setup
```

### Database errors
```bash
just db-reset
just db-init
```

### Port already in use
```bash
# Use a different port
just serve 0.0.0.0 8080
```

### Can't connect to Ollama
```bash
# Check if Ollama is running
ollama list

# Start Ollama
just ollama-start

# Check .env for correct OLLAMA_HOST
```

## Next Steps

- Read [LOCAL_DEV.md](./LOCAL_DEV.md) for detailed development guide
- Read [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines
- Explore [API_EXAMPLES.md](./API_EXAMPLES.md) for API usage examples
- Check [README.md](./README.md) for project overview

## Need Help?

- Run `just info` to see your environment info
- Run `just verify` to check your setup
- Check the documentation files mentioned above
- Open an issue on GitHub

## Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/tutorial/
- **SQLAlchemy**: https://docs.sqlalchemy.org/en/20/
- **Ollama**: https://ollama.ai/docs
- **uv**: https://github.com/astral-sh/uv
- **just**: https://just.systems/man/

---

Happy coding! 🚀

If you found this helpful, consider giving the project a ⭐ on GitHub!

