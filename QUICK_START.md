# Quick Start Guide

Get up and running with the BKU LLM Platform in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- Git installed
- 8GB+ RAM recommended
- 10GB+ free disk space

## Installation (3 Steps)

### Step 1: Setup

```bash
# Clone the repository (if not already done)
cd /home/erkin/.cursor/worktrees/kishai/bku

# Run the setup script
./scripts/setup.sh
```

This will:
- Create `.env` file with secure credentials
- Start all Docker containers
- Pull the default llama2 model

### Step 2: Access the Platform

Open your browser and go to:
- **Frontend:** http://localhost
- **API Docs:** http://localhost:8000/docs

### Step 3: Create Your Account

1. Click "Register" on the login page
2. Fill in your details:
   - Username: `your-username`
   - Email: `your@email.com`
   - Password: `secure-password` (min 8 characters)
3. Click "Create account"
4. Login with your credentials

## First Time Use

### 1. Create a Deployment

Go to **Deployments** page and click "Add Deployment":

```
Name: Local Ollama
Host: http://ollama
Port: 11434
Type: on_premise
Description: Local development deployment
```

Click "Create" - the platform will automatically check the health.

### 2. Test Inference

Go to **Inference** page:

1. Select deployment: "Local Ollama"
2. Select model: "llama2"
3. Type a message: "Hello, how are you?"
4. Click Send!

### 3. Generate an API Key

Go to **API Keys** page:

1. Click "Create API Key"
2. Name: "My First Key"
3. Expiration: 365 days
4. Click "Create"
5. **IMPORTANT:** Copy the key immediately (you won't see it again!)

### 4. Use the API

```bash
# Test your API key
curl -X POST "http://localhost:8000/api/v1/inference/chat/api-key" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "messages": [{"role": "user", "content": "What is AI?"}],
    "model": "llama2"
  }'
```

## Common Commands

### View Logs
```bash
# All logs
docker-compose logs -f

# Backend only
docker logs -f bku-backend

# Ollama only
docker logs -f bku-ollama
```

### Manage Ollama Models
```bash
# List installed models
docker exec bku-ollama ollama list

# Pull a new model
docker exec bku-ollama ollama pull mistral

# Remove a model
docker exec bku-ollama ollama rm llama2
```

### Start/Stop/Restart
```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Restart a specific service
docker-compose restart backend
```

### Create Admin User (Optional)
```bash
cd /home/erkin/.cursor/worktrees/kishai/bku
python scripts/init-admin.py
```

## Platform Overview

### Dashboard
- View system metrics
- Monitor deployments
- Check success rates
- Track token usage

### Deployments
- Manage Ollama instances
- Add cloud/on-premise deployments
- Monitor health status
- Configure endpoints

### Models
- Register model metadata
- Track versions
- Upload model files
- Set visibility (public/private)

### Inference
- Interactive chat interface
- Select deployment & model
- Real-time responses
- Conversation history

### API Keys
- Generate keys for programmatic access
- Set expiration dates
- Monitor usage
- Revoke keys

### Monitoring
- View request metrics
- Track performance
- Analyze usage patterns
- View audit logs

## Python Client Example

```python
import requests

API_KEY = "your-api-key-here"
BASE_URL = "http://localhost:8000/api/v1"

def chat(message):
    response = requests.post(
        f"{BASE_URL}/inference/chat/api-key",
        headers={"X-API-Key": API_KEY},
        json={
            "messages": [{"role": "user", "content": message}],
            "model": "llama2"
        }
    )
    return response.json()["content"]

# Usage
answer = chat("What is machine learning?")
print(answer)
```

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker logs bku-backend

# Verify .env file exists
cat .env

# Restart
docker-compose restart backend
```

### Can't connect to Ollama
```bash
# Check if Ollama is running
docker ps | grep ollama

# Test connection
curl http://localhost:11434/api/tags

# Restart Ollama
docker-compose restart ollama
```

### Model not found
```bash
# List available models
docker exec bku-ollama ollama list

# Pull the model
docker exec bku-ollama ollama pull llama2
```

### Frontend errors
```bash
# Check if backend is running
curl http://localhost:8000/health

# Clear browser cache
# Refresh the page
```

## Production Deployment

For production deployment, see:
- `DEPLOYMENT.md` - Comprehensive deployment guide
- `README.md` - Full documentation

Key steps:
1. Use PostgreSQL instead of SQLite
2. Set strong `SECRET_KEY` in `.env`
3. Configure TLS/SSL with reverse proxy
4. Enable rate limiting
5. Set up backups
6. Configure monitoring

## Next Steps

1. ✅ Explore the dashboard
2. ✅ Create multiple deployments
3. ✅ Add custom models
4. ✅ Test the inference API
5. ✅ Review monitoring metrics
6. ✅ Read the full documentation

## Support

- **Documentation:** See `README.md` and `DEPLOYMENT.md`
- **API Examples:** See `API_EXAMPLES.md`
- **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`

## Useful Links

- API Documentation: http://localhost:8000/docs
- Alternative API Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
- Ollama API: http://localhost:11434

## Default Credentials (if using init-admin.py)

```
Username: admin
Password: admin123
Email: admin@example.com
```

**Important:** Change these credentials after first login!

---

**Congratulations! 🎉**

You now have a fully functional LLM deployment platform running locally!

