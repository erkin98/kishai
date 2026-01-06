# Quick Reference Card

One-page reference for daily development with Kishai.

## 🚀 First Time Setup

```bash
# Install tools
curl -LsSf https://astral.sh/uv/install.sh | sh
cargo install just  # or: brew install just

# Setup project
./SETUP.sh

# Start developing
source .venv/bin/activate
just dev
```

## 📋 Most Used Commands

| Command | Description |
|---------|-------------|
| `just` | List all available commands |
| `just dev` | Start development server |
| `just test` | Run tests |
| `just test-cov` | Run tests with coverage |
| `just fmt` | Format code |
| `just lint` | Lint code |
| `just check` | Run all quality checks |
| `just clean` | Clean generated files |

## 🗄️ Database Commands

| Command | Description |
|---------|-------------|
| `just db-init` | Initialize database |
| `just db-reset` | Reset database (⚠️ deletes data) |
| `just migrate "msg"` | Create new migration |
| `just migrate-up` | Apply migrations |
| `just migrate-down` | Rollback last migration |

## 🤖 Ollama Commands

| Command | Description |
|---------|-------------|
| `just ollama-start` | Start Ollama service |
| `just ollama-pull MODEL` | Pull a model (e.g., llama2) |
| `just ollama-list` | List installed models |

## 🔧 Utility Commands

| Command | Description |
|---------|-------------|
| `just info` | Show project information |
| `just verify` | Verify setup |
| `just secret` | Generate SECRET_KEY |
| `just env` | Create .env from template |
| `just hooks` | Install pre-commit hooks |
| `just upgrade` | Upgrade dependencies |
| `just clean-all` | Clean everything including venv |

## 📂 Project Structure

```
backend/app/
├── api/          # API endpoints (add routes here)
├── auth/         # Authentication logic
├── models/       # Database models
├── services/     # Business logic
├── middleware/   # Custom middleware
├── utils/        # Helper functions
├── config.py     # Configuration
├── database.py   # Database setup
└── main.py       # FastAPI app

tests/            # Test files
scripts/          # Utility scripts
```

## 🔑 Environment Variables

Essential variables in `.env`:

```bash
SECRET_KEY="generate-with-just-secret"
DATABASE_URL="sqlite+aiosqlite:///./bku.db"
DEFAULT_OLLAMA_HOST="http://localhost:11434"
DEBUG=false
```

## 🧪 Testing

```bash
# Run all tests
just test

# With coverage report
just test-cov

# Watch mode (auto-rerun)
just test-watch

# Specific test file
pytest tests/test_auth.py

# Specific test function
pytest tests/test_auth.py::test_user_registration
```

## 🎨 Code Quality

```bash
# Format code (automatic fix)
just fmt

# Lint code (show issues)
just lint

# Type check
just typecheck

# Run all checks
just check
```

## 📝 Git Workflow

```bash
# 1. Make changes
vim backend/app/api/my_endpoint.py

# 2. Format and check
just fmt
just check

# 3. Test
just test

# 4. Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: add new endpoint"

# 5. Push
git push
```

## 🔍 Debugging

```bash
# Check if tools are installed
just check-tools

# Verify complete setup
just verify

# Show environment info
just info

# View logs (when server is running)
# Check terminal output

# Test Ollama connection
curl http://localhost:11434/api/tags
```

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| `just: command not found` | Install just: `cargo install just` |
| `uv: command not found` | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Import errors | Run `just install` to sync dependencies |
| Database errors | Run `just db-reset` then `just db-init` |
| Port in use | Use `just serve 0.0.0.0 8080` |
| Virtual env issues | Run `just clean-all` then `just setup` |

## 📍 Important URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000 | API root |
| http://localhost:8000/docs | Interactive API docs (Swagger) |
| http://localhost:8000/redoc | Alternative API docs |
| http://localhost:11434 | Ollama service |

## 📖 Documentation Files

| File | When to Read |
|------|-------------|
| [GETTING_STARTED.md](./GETTING_STARTED.md) | First time setup |
| [LOCAL_DEV.md](./LOCAL_DEV.md) | Development details |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Before contributing |
| [API_EXAMPLES.md](./API_EXAMPLES.md) | API usage examples |
| [DEV_TOOLS_OVERVIEW.md](./DEV_TOOLS_OVERVIEW.md) | Visual overview |

## 🎯 Daily Workflow

```bash
# Morning routine
cd kishai
source .venv/bin/activate
just dev                    # In one terminal

# In another terminal
just test-watch             # Auto-run tests

# Before lunch
just check                  # Run all quality checks

# Before going home
just test
git add .
git commit -m "feat: today's work"
git push
```

## 💡 Pro Tips

1. **Alias common commands** in your `.bashrc` or `.zshrc`:
   ```bash
   alias jd="just dev"
   alias jt="just test"
   alias jf="just fmt"
   alias jc="just check"
   ```

2. **Use watch mode** for tests while developing:
   ```bash
   just test-watch
   ```

3. **Check setup anytime**:
   ```bash
   just verify
   ```

4. **Generate secure keys easily**:
   ```bash
   just secret >> .env
   ```

5. **Explore available commands**:
   ```bash
   just | grep -A 100 "Available recipes:"
   ```

## 🔗 Quick Links

- Repo: [GitHub](https://github.com/yourusername/kishai)
- FastAPI: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- Ollama: [ollama.ai](https://ollama.ai)
- uv: [github.com/astral-sh/uv](https://github.com/astral-sh/uv)
- just: [just.systems](https://just.systems)

---

**Print this page and keep it next to your monitor!** 📄✨

Or bookmark it in your browser: `file:///path/to/kishai/QUICK_REFERENCE.md`

