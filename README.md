# BKU - Custom LLM Deployment Platform

Enterprise-grade platform for deploying and managing custom-trained LLMs with high-level security and privacy. Supports both cloud and on-premise deployments with unified management.

## Features

- **🔐 Enterprise Security**: JWT authentication, API keys, data encryption at rest and in transit
- **☁️ Multi-Deployment**: Support for cloud, on-premise, and hybrid deployments
- **🤖 Model Management**: Upload, version, and deploy custom LLM models
- **📊 Monitoring**: Comprehensive metrics, logging, and usage tracking
- **🎯 Inference Playground**: Interactive testing interface for your models
- **🔑 API Access**: RESTful API with programmatic access via API keys
- **🎨 Modern UI**: Beautiful, responsive React dashboard

## Architecture

```
┌─────────────┐
│   Frontend  │  React + Vite + TypeScript
│  Dashboard  │  
└──────┬──────┘
       │
       ├── REST API ──────┐
       │                  │
┌──────▼──────┐    ┌─────▼─────┐
│   Backend   │    │  Ollama   │
│   FastAPI   │◄───┤  Runtime  │
│   Python    │    │           │
└──────┬──────┘    └───────────┘
       │
┌──────▼──────┐
│   SQLite    │
│  Database   │
└─────────────┘
```

## Tech Stack

### Backend
- **FastAPI**: Modern, async Python web framework
- **SQLAlchemy**: ORM with async support
- **Ollama**: LLM inference backend
- **JWT**: Token-based authentication
- **Cryptography**: Data encryption

### Frontend
- **React 18**: Modern UI library
- **Vite**: Fast build tool
- **TypeScript**: Type-safe JavaScript
- **TanStack Query**: Data fetching and caching
- **Zustand**: State management
- **Tailwind CSS**: Utility-first styling

## Quick Start

### 📚 Documentation

- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - ⭐ One-page command reference
- **[GETTING_STARTED.md](./GETTING_STARTED.md)** - First time setup guide
- **[LOCAL_DEV.md](./LOCAL_DEV.md)** - Complete development guide  
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - How to contribute
- **[DEV_TOOLS_OVERVIEW.md](./DEV_TOOLS_OVERVIEW.md)** - Visual tools overview
- **[DEV_SETUP_SUMMARY.md](./DEV_SETUP_SUMMARY.md)** - What was added to the project
- **[API_EXAMPLES.md](./API_EXAMPLES.md)** - API usage examples
- **[CHANGES.md](./CHANGES.md)** - Complete list of changes

### Prerequisites

#### For Local Development (Recommended)
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (fast package manager)
- [just](https://just.systems) (command runner)
- [Ollama](https://ollama.ai) (for LLM inference)

See [GETTING_STARTED.md](./GETTING_STARTED.md) for installation instructions.

#### For Docker Deployment
- Docker & Docker Compose
- Git

### Local Development Setup

```bash
# Quick start (automated)
./SETUP.sh

# Or manual setup
just setup          # Create venv and install deps
just env            # Create .env file
just db-init        # Initialize database
just dev            # Start development server
```

**See [GETTING_STARTED.md](./GETTING_STARTED.md) for detailed instructions.**

### Docker Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd bku
```

2. **Create environment file**
```bash
cp .env.example .env
```

Edit `.env` and set your configuration:
```env
SECRET_KEY=<generate-with-openssl-rand-hex-32>
DATABASE_URL=sqlite+aiosqlite:////data/bku.db
```

3. **Start the platform**
```bash
docker-compose up -d
```

4. **Access the platform**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Ollama: http://localhost:11434

5. **Pull an Ollama model** (from inside the container)
```bash
docker exec -it bku-ollama ollama pull llama2
```

## Development Setup

### Modern Setup (Recommended) - Using uv and just

**Prerequisites**: Python 3.11+, [uv](https://github.com/astral-sh/uv), [just](https://just.systems)

```bash
# Quick start - setup and run
just start

# Or step by step:
just setup          # Setup virtual environment
just env            # Create .env file
just db-init        # Initialize database
just dev            # Start development server
```

See [LOCAL_DEV.md](./LOCAL_DEV.md) for detailed instructions.

### Traditional Setup

#### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:5173

## Usage Guide

### 1. Register an Account

Navigate to http://localhost and click "Register" to create an account.

### 2. Create a Deployment

1. Go to "Deployments" page
2. Click "Add Deployment"
3. Configure your deployment:
   - **Name**: e.g., "Local Ollama"
   - **Host**: http://ollama
   - **Port**: 11434
   - **Type**: Choose cloud/on-premise/hybrid
4. Click "Create"

### 3. Add Models

1. Go to "Models" page
2. Click "Add Model"
3. Enter model details:
   - **Name**: Unique identifier
   - **Display Name**: Human-readable name
   - **Base Model**: e.g., "llama2"
   - **Parameters**: e.g., "7B"

### 4. Test Inference

1. Go to "Inference" page
2. Select your deployment
3. Select a model (e.g., "llama2")
4. Start chatting!

### 5. Generate API Keys

1. Go to "API Keys" page
2. Click "Create API Key"
3. Give it a name and expiration
4. Copy the key (you won't see it again!)

### 6. Use the API

```python
import requests

API_KEY = "your-api-key-here"
url = "http://localhost:8000/api/v1/inference/chat/api-key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

data = {
    "messages": [
        {"role": "user", "content": "Hello, how are you?"}
    ],
    "model": "llama2"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/api-keys` - Create API key
- `GET /api/v1/auth/api-keys` - List API keys
- `DELETE /api/v1/auth/api-keys/{id}` - Revoke API key

### Inference
- `POST /api/v1/inference/chat` - Chat completion
- `POST /api/v1/inference/chat/stream` - Streaming chat
- `GET /api/v1/inference/models` - List available models

### Deployments
- `GET /api/v1/deployments` - List deployments
- `POST /api/v1/deployments` - Create deployment (admin)
- `GET /api/v1/deployments/{id}` - Get deployment
- `PUT /api/v1/deployments/{id}` - Update deployment (admin)
- `DELETE /api/v1/deployments/{id}` - Delete deployment (admin)
- `GET /api/v1/deployments/{id}/health` - Check health

### Models
- `GET /api/v1/models` - List models
- `POST /api/v1/models` - Create model (admin)
- `GET /api/v1/models/{id}` - Get model
- `PUT /api/v1/models/{id}` - Update model (admin)
- `GET /api/v1/models/{id}/versions` - List versions
- `POST /api/v1/models/{id}/versions` - Create version (admin)
- `POST /api/v1/models/{id}/upload` - Upload model file (admin)

### Monitoring
- `GET /api/v1/monitoring/metrics` - System metrics (admin)
- `GET /api/v1/monitoring/deployments/{id}/metrics` - Deployment metrics (admin)
- `GET /api/v1/monitoring/usage` - User usage stats
- `GET /api/v1/monitoring/logs` - All logs (admin)
- `GET /api/v1/monitoring/my-logs` - User's logs

## Security Features

### Authentication & Authorization
- JWT tokens with configurable expiration
- API keys for programmatic access
- Role-based access control (admin/user)

### Data Protection
- AES-256 encryption for sensitive data at rest
- TLS/SSL for data in transit (configure reverse proxy)
- Secure password hashing with bcrypt
- API key encryption in database

### Isolation & Auditing
- Per-request tracking with unique IDs
- Comprehensive audit logging
- Sensitive data redaction in logs
- Input validation and sanitization

### Rate Limiting
- Configurable rate limits per user
- Protection against abuse
- DDoS mitigation

## Deployment Options

### Cloud Deployment (AWS/GCP/Azure)

1. Use managed Kubernetes (EKS/GKE/AKS)
2. Deploy with Kubernetes manifests or Helm
3. Use managed databases (RDS/Cloud SQL)
4. Configure TLS with Let's Encrypt or cloud certificates

### On-Premise Deployment

1. Use Docker Compose or Kubernetes
2. Connect to local Ollama instances
3. Store data in local databases
4. Configure internal TLS certificates

### Hybrid Deployment

1. Deploy backend in cloud
2. Connect to on-premise Ollama instances via VPN
3. Benefit from cloud management with on-premise privacy

## Configuration

### Environment Variables

See `.env.example` for all available configuration options:

- `SECRET_KEY`: JWT signing key (required)
- `DATABASE_URL`: Database connection string
- `ENCRYPTION_KEY`: Encryption key for sensitive data
- `CORS_ORIGINS`: Allowed CORS origins
- `RATE_LIMIT_PER_MINUTE`: API rate limit
- `DEFAULT_OLLAMA_HOST`: Default Ollama endpoint

### Database Migration

Using Alembic for schema migrations:

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Monitoring & Logging

### View Logs

```bash
# Backend logs
docker logs -f bku-backend

# Ollama logs
docker logs -f bku-ollama

# All logs
docker-compose logs -f
```

### Metrics

Access the Monitoring page in the dashboard for:
- Request counts and success rates
- Average latency and throughput
- Token usage statistics
- Per-deployment metrics
- User usage tracking

## Troubleshooting

### Backend won't start
- Check logs: `docker logs bku-backend`
- Verify database connection
- Ensure SECRET_KEY is set

### Ollama connection fails
- Verify Ollama is running: `docker ps | grep ollama`
- Check deployment configuration
- Test connection: `curl http://localhost:11434/api/tags`

### Frontend can't reach backend
- Check CORS configuration
- Verify nginx proxy settings
- Check network connectivity

### Model not available
- Pull model: `docker exec -it bku-ollama ollama pull <model-name>`
- List models: `docker exec -it bku-ollama ollama list`

## Production Recommendations

1. **Use PostgreSQL** instead of SQLite for production
2. **Configure TLS/SSL** with proper certificates
3. **Set strong SECRET_KEY** (32+ random bytes)
4. **Enable rate limiting** appropriately
5. **Use a reverse proxy** (nginx/Traefik) with TLS
6. **Configure backups** for database and models
7. **Monitor system resources** and scale as needed
8. **Use secrets management** (Vault, AWS Secrets Manager)
9. **Enable audit logging** and monitoring
10. **Regular security updates** for all components

## Development Commands

When using the modern dev setup with `just`:

```bash
just              # List all commands
just dev          # Start dev server
just test         # Run tests
just fmt          # Format code
just check        # Run all checks
just clean        # Clean generated files
```

See the [justfile](./justfile) for all available commands.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

MIT License - See LICENSE file for details

## Support

- 📖 Documentation: See the docs listed at the top of this README
- 🐛 Bug Reports: Open an issue on GitHub
- 💡 Feature Requests: Open an issue on GitHub
- 💬 Questions: Check [GETTING_STARTED.md](./GETTING_STARTED.md) and [LOCAL_DEV.md](./LOCAL_DEV.md)

## Credits

Built with:
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend library
- [shadcn/ui](https://ui.shadcn.com/) - UI components inspiration

