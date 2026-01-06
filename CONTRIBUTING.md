# Contributing to Kishai

Thank you for your interest in contributing to Kishai! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/kishai.git
   cd kishai
   ```

2. **Setup development environment**
   ```bash
   just setup
   # or run SETUP.sh
   ./SETUP.sh
   ```

3. **Configure your environment**
   ```bash
   just env
   # Edit .env with your settings
   ```

4. **Install pre-commit hooks**
   ```bash
   just hooks
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

3. **Format and lint your code**
   ```bash
   just fmt    # Format code
   just check  # Run all checks
   ```

4. **Run tests**
   ```bash
   just test
   # or with coverage
   just test-cov
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Build process or auxiliary tool changes

Examples:
```
feat: add streaming support for chat API
fix: resolve authentication token expiration issue
docs: update API documentation for inference endpoint
```

### Pull Request Process

1. **Update documentation** if needed
2. **Ensure all tests pass**: `just test`
3. **Run code quality checks**: `just check`
4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request** on GitHub
6. **Wait for review** - maintainers will review your PR

## Code Style

### Python

- **Line length**: 100 characters
- **Formatter**: Ruff
- **Linter**: Ruff
- **Type checker**: mypy
- **Docstrings**: Google style

Example:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")
    return True
```

### Running Code Quality Tools

```bash
# Format code
just fmt

# Lint code
just lint

# Type check
just typecheck

# Run all checks
just check
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Use fixtures for common setup

Example:
```python
@pytest.mark.asyncio
async def test_user_registration_success(client: AsyncClient):
    """Test successful user registration"""
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepass123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
```

### Running Tests

```bash
# Run all tests
just test

# Run with coverage
just test-cov

# Run specific test file
pytest tests/test_auth.py

# Run tests in watch mode
just test-watch
```

## Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Update API_EXAMPLES.md for API changes
- Update LOCAL_DEV.md for development setup changes
- Add docstrings to all functions and classes
- Update type hints

### Building API Documentation

The API documentation is automatically generated from the FastAPI app:
- Start the dev server: `just dev`
- Visit http://localhost:8000/docs

## Database Changes

### Creating Migrations

```bash
# Create a new migration
just migrate "description of change"

# Apply migrations
just migrate-up

# Rollback migration
just migrate-down
```

## Project Structure

```
kishai/
├── backend/
│   └── app/
│       ├── api/          # API endpoints
│       ├── auth/         # Authentication
│       ├── models/       # Database models
│       ├── services/     # Business logic
│       ├── middleware/   # Custom middleware
│       └── utils/        # Utilities
├── tests/                # Test files
├── scripts/              # Utility scripts
├── pyproject.toml        # Dependencies (uv)
├── justfile              # Task automation (just)
└── LOCAL_DEV.md          # Development guide
```

## Getting Help

- Check [LOCAL_DEV.md](./LOCAL_DEV.md) for setup issues
- Check [README.md](./README.md) for general information
- Open an issue on GitHub for bugs
- Ask questions in discussions

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help create a welcoming environment

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

## Questions?

Feel free to open an issue or reach out to the maintainers!

Thank you for contributing to Kishai! 🎉

