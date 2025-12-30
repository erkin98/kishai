# Deployment Guide

This guide covers various deployment scenarios for the BKU LLM Platform.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Compose Deployment](#docker-compose-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [On-Premise Deployment](#on-premise-deployment)
5. [Security Hardening](#security-hardening)

---

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL="sqlite+aiosqlite:///./bku.db"
export DEFAULT_OLLAMA_HOST="http://localhost:11434"

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Ollama (Separate Terminal)

```bash
# Install Ollama from https://ollama.ai
ollama serve

# Pull a model
ollama pull llama2
```

---

## Docker Compose Deployment

### Basic Setup

```bash
# Clone repository
git clone <repo-url>
cd bku

# Create environment file
cp .env.example .env

# Generate secret key
openssl rand -hex 32

# Edit .env with your configuration
nano .env

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Pull Ollama Models

```bash
docker exec -it bku-ollama ollama pull llama2
docker exec -it bku-ollama ollama pull mistral
docker exec -it bku-ollama ollama list
```

### Access Services

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Ollama: http://localhost:11434

---

## Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Build and Push Images**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -t bku-backend .
docker tag bku-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/bku-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/bku-backend:latest

# Build and push frontend
cd ../frontend
docker build -t bku-frontend .
docker tag bku-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/bku-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/bku-frontend:latest
```

2. **Create RDS Database** (PostgreSQL)

```bash
aws rds create-db-instance \
  --db-instance-identifier bku-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password <secure-password> \
  --allocated-storage 20
```

3. **Create ECS Task Definition**

```json
{
  "family": "bku-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/bku-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql+asyncpg://admin:<password>@<rds-endpoint>/bku"
        },
        {
          "name": "SECRET_KEY",
          "value": "<your-secret-key>"
        }
      ]
    }
  ]
}
```

4. **Setup Load Balancer and CloudFront**

#### Using Kubernetes (EKS)

See `kubernetes/` directory for manifests.

```bash
# Create cluster
eksctl create cluster --name bku-cluster --region us-east-1

# Apply manifests
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/ingress.yaml
```

### GCP Deployment

1. **Build with Cloud Build**

```bash
gcloud builds submit --config cloudbuild.yaml
```

2. **Deploy to Cloud Run**

```bash
# Backend
gcloud run deploy bku-backend \
  --image gcr.io/<project-id>/bku-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Frontend
gcloud run deploy bku-frontend \
  --image gcr.io/<project-id>/bku-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

1. **Create Container Registry**

```bash
az acr create --resource-group bku-rg --name bkuacr --sku Basic
```

2. **Push Images**

```bash
az acr build --registry bkuacr --image bku-backend:latest ./backend
az acr build --registry bkuacr --image bku-frontend:latest ./frontend
```

3. **Deploy to Container Instances or AKS**

---

## On-Premise Deployment

### Using Docker Compose

1. **Hardware Requirements**
   - CPU: 8+ cores
   - RAM: 16GB+ (32GB recommended for large models)
   - Storage: 100GB+ SSD
   - GPU: NVIDIA GPU with 8GB+ VRAM (optional, for better performance)

2. **Install Docker**

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# For GPU support
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
```

3. **Deploy**

```bash
# Clone repository
git clone <repo-url>
cd bku

# Configure
cp .env.example .env
nano .env  # Edit configuration

# For GPU support, edit docker-compose.yml and uncomment GPU section

# Deploy
docker-compose up -d

# Setup TLS with Let's Encrypt (optional)
docker-compose -f docker-compose.yml -f docker-compose.tls.yml up -d
```

### Using Kubernetes (On-Premise)

1. **Setup K3s or kubeadm cluster**

```bash
# K3s (lightweight)
curl -sfL https://get.k3s.io | sh -

# Configure kubectl
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

2. **Deploy application**

```bash
kubectl apply -f kubernetes/
```

---

## Security Hardening

### 1. TLS/SSL Configuration

#### Using Let's Encrypt with Traefik

```yaml
# docker-compose.tls.yml
version: '3.8'
services:
  traefik:
    image: traefik:v2.10
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./traefik.yml:/traefik.yml
      - ./acme.json:/acme.json
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.email=your@email.com"
      - "--certificatesresolvers.myresolver.acme.storage=/acme.json"
      - "--certificatesresolvers.myresolver.acme.httpchallenge.entrypoint=web"
```

### 2. Database Security

#### Use PostgreSQL in Production

```env
DATABASE_URL=postgresql+asyncpg://username:password@postgres:5432/bku
```

#### Enable SSL

```python
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?ssl=require
```

### 3. API Security

#### Rate Limiting

```env
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
```

#### IP Whitelisting

Configure in reverse proxy (nginx/Traefik).

### 4. Secrets Management

#### Using Docker Secrets

```yaml
secrets:
  secret_key:
    external: true

services:
  backend:
    secrets:
      - secret_key
    environment:
      SECRET_KEY_FILE: /run/secrets/secret_key
```

#### Using Vault

```bash
# Store secret in Vault
vault kv put secret/bku secret_key="your-secret-key"

# Configure backend to read from Vault
export VAULT_ADDR="http://vault:8200"
export VAULT_TOKEN="your-vault-token"
```

### 5. Network Security

#### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

#### Internal Network Isolation

Use Docker networks or Kubernetes network policies.

### 6. Monitoring & Logging

#### Setup Prometheus & Grafana

```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

#### Centralized Logging (ELK Stack)

```yaml
services:
  elasticsearch:
    image: elasticsearch:8.11.0
  
  logstash:
    image: logstash:8.11.0
  
  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
```

### 7. Backup Strategy

```bash
# Database backup
docker exec bku-backend pg_dump -U postgres bku > backup-$(date +%Y%m%d).sql

# Model storage backup
tar -czf models-backup-$(date +%Y%m%d).tar.gz models/

# Automated backup with cron
0 2 * * * /path/to/backup-script.sh
```

---

## Health Checks & Monitoring

### Endpoint Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Ollama health
curl http://localhost:11434/api/tags
```

### Docker Health Checks

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## Scaling

### Horizontal Scaling

```bash
# Scale backend replicas
docker-compose up -d --scale backend=3

# Kubernetes scaling
kubectl scale deployment bku-backend --replicas=3
```

### Load Balancing

Configure in nginx or cloud load balancer.

---

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check DATABASE_URL
   - Verify database is running
   - Check network connectivity

2. **Ollama not responding**
   - Verify Ollama is running
   - Check deployment configuration
   - Ensure models are pulled

3. **Out of memory**
   - Reduce model size
   - Increase system RAM
   - Configure swap space

4. **Slow inference**
   - Use GPU acceleration
   - Reduce model size
   - Increase hardware resources

---

## Maintenance

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Database Migrations

```bash
docker exec bku-backend alembic upgrade head
```

### Clean Up

```bash
# Remove unused images
docker system prune -a

# Remove old logs
docker-compose logs --tail=0 backend > /dev/null
```

