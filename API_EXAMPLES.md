# API Usage Examples

This document provides practical examples for using the BKU Platform API.

## Authentication

### Register a New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Create API Key

```bash
curl -X POST "http://localhost:8000/api/v1/auth/api-keys" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Production API",
    "expires_in_days": 365
  }'
```

Response:
```json
{
  "id": 1,
  "name": "Production API",
  "key": "bku_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "is_active": true,
  "expires_at": "2025-12-30T00:00:00",
  "created_at": "2024-12-30T00:00:00"
}
```

## Deployments

### Create a Deployment

```bash
curl -X POST "http://localhost:8000/api/v1/deployments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Production Ollama",
    "host": "http://ollama-prod.example.com",
    "port": 11434,
    "deployment_type": "cloud",
    "description": "Production cloud deployment"
  }'
```

### List All Deployments

```bash
curl -X GET "http://localhost:8000/api/v1/deployments" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Check Deployment Health

```bash
curl -X GET "http://localhost:8000/api/v1/deployments/1/health" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Inference

### Chat Completion (JWT Auth)

```bash
curl -X POST "http://localhost:8000/api/v1/inference/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is machine learning?"}
    ],
    "model": "llama2",
    "deployment_id": 1
  }'
```

### Chat Completion (API Key Auth)

```bash
curl -X POST "http://localhost:8000/api/v1/inference/chat/api-key" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: bku_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain quantum computing"}
    ],
    "model": "llama2"
  }'
```

### List Available Models

```bash
curl -X GET "http://localhost:8000/api/v1/inference/models?deployment_id=1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Python Examples

### Basic Usage

```python
import requests

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "bku_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Chat completion
def chat(message: str, model: str = "llama2"):
    response = requests.post(
        f"{BASE_URL}/inference/chat/api-key",
        headers=headers,
        json={
            "messages": [{"role": "user", "content": message}],
            "model": model
        }
    )
    return response.json()

# Example usage
result = chat("What is the capital of France?")
print(result["content"])
```

### Complete Client Class

```python
import requests
from typing import List, Dict, Optional


class BKUClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        deployment_id: Optional[int] = None
    ) -> Dict:
        """Send a chat completion request"""
        response = requests.post(
            f"{self.base_url}/inference/chat/api-key",
            headers=self.headers,
            json={
                "messages": messages,
                "model": model,
                "deployment_id": deployment_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    def list_models(self, deployment_id: Optional[int] = None) -> List[str]:
        """List available models"""
        params = {"deployment_id": deployment_id} if deployment_id else {}
        response = requests.get(
            f"{self.base_url}/inference/models",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()["models"]
    
    def list_deployments(self) -> List[Dict]:
        """List all deployments"""
        response = requests.get(
            f"{self.base_url}/deployments",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_usage(self, days: int = 30) -> Dict:
        """Get usage statistics"""
        response = requests.get(
            f"{self.base_url}/monitoring/usage",
            headers=self.headers,
            params={"days": days}
        )
        response.raise_for_status()
        return response.json()


# Usage
client = BKUClient(
    base_url="http://localhost:8000/api/v1",
    api_key="bku_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
)

# Simple chat
response = client.chat(
    messages=[{"role": "user", "content": "Hello!"}],
    model="llama2"
)
print(response["content"])

# List available models
models = client.list_models()
print("Available models:", models)

# Get usage stats
usage = client.get_usage(days=7)
print(f"Requests last 7 days: {usage['total_requests']}")
print(f"Tokens used: {usage['total_tokens']}")
```

## JavaScript/Node.js Examples

### Basic Usage

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/v1';
const API_KEY = 'bku_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx';

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  }
});

// Chat completion
async function chat(message, model = 'llama2') {
  const response = await client.post('/inference/chat/api-key', {
    messages: [{ role: 'user', content: message }],
    model: model
  });
  return response.data;
}

// Example usage
(async () => {
  const result = await chat('What is artificial intelligence?');
  console.log(result.content);
})();
```

### Complete Client Class

```javascript
class BKUClient {
  constructor(baseURL, apiKey) {
    this.client = axios.create({
      baseURL: baseURL,
      headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json'
      }
    });
  }

  async chat(messages, model, deploymentId = null) {
    const response = await this.client.post('/inference/chat/api-key', {
      messages,
      model,
      deployment_id: deploymentId
    });
    return response.data;
  }

  async listModels(deploymentId = null) {
    const params = deploymentId ? { deployment_id: deploymentId } : {};
    const response = await this.client.get('/inference/models', { params });
    return response.data.models;
  }

  async listDeployments() {
    const response = await this.client.get('/deployments');
    return response.data;
  }

  async getUsage(days = 30) {
    const response = await this.client.get('/monitoring/usage', {
      params: { days }
    });
    return response.data;
  }
}

// Usage
const client = new BKUClient(
  'http://localhost:8000/api/v1',
  'bku_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
);

(async () => {
  // Simple chat
  const response = await client.chat(
    [{ role: 'user', content: 'Hello!' }],
    'llama2'
  );
  console.log(response.content);

  // List models
  const models = await client.listModels();
  console.log('Available models:', models);

  // Get usage
  const usage = await client.getUsage(7);
  console.log(`Requests (7 days): ${usage.total_requests}`);
  console.log(`Tokens used: ${usage.total_tokens}`);
})();
```

## Monitoring

### Get System Metrics

```bash
curl -X GET "http://localhost:8000/api/v1/monitoring/metrics?days=7" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get User Usage

```bash
curl -X GET "http://localhost:8000/api/v1/monitoring/usage?days=30" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Recent Logs

```bash
curl -X GET "http://localhost:8000/api/v1/monitoring/my-logs?limit=50" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Model Management

### Create a Model

```bash
curl -X POST "http://localhost:8000/api/v1/models" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "custom-llama2",
    "display_name": "Custom LLaMA 2",
    "description": "Fine-tuned LLaMA 2 model",
    "base_model": "llama2",
    "parameters": "7B",
    "is_public": false
  }'
```

### List Models

```bash
curl -X GET "http://localhost:8000/api/v1/models?is_active=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Upload Model File

```bash
curl -X POST "http://localhost:8000/api/v1/models/1/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/model.gguf"
```

## Error Handling

### Python Example

```python
import requests
from requests.exceptions import HTTPError

def safe_chat(message: str):
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/inference/chat/api-key",
            headers={"X-API-Key": API_KEY},
            json={
                "messages": [{"role": "user", "content": message}],
                "model": "llama2"
            }
        )
        response.raise_for_status()
        return response.json()
    except HTTPError as e:
        if e.response.status_code == 401:
            print("Authentication failed. Check your API key.")
        elif e.response.status_code == 404:
            print("Model or deployment not found.")
        elif e.response.status_code == 500:
            print("Server error. Please try again later.")
        else:
            print(f"Error: {e.response.text}")
        return None
```

## Rate Limiting

If you encounter rate limiting errors (429), implement exponential backoff:

```python
import time
import requests

def chat_with_retry(message: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/inference/chat/api-key",
                headers={"X-API-Key": API_KEY},
                json={
                    "messages": [{"role": "user", "content": message}],
                    "model": "llama2"
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

## WebSocket Streaming (Future)

Note: Streaming is currently available via Server-Sent Events (SSE). WebSocket support may be added in future versions.

```python
import requests

def stream_chat(message: str):
    response = requests.post(
        "http://localhost:8000/api/v1/inference/chat/stream",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "messages": [{"role": "user", "content": message}],
            "model": "llama2"
        },
        stream=True
    )
    
    for line in response.iter_lines():
        if line:
            data = line.decode('utf-8')
            if data.startswith('data: '):
                chunk = data[6:]  # Remove 'data: ' prefix
                if chunk == '[DONE]':
                    break
                print(chunk, end='', flush=True)
```

