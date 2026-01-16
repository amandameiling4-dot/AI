# CodeAI Deployment Guide

Production deployment and operational runbooks for CodeAI.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [AWS Deployment](#aws-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring & Observability](#monitoring--observability)
7. [Scaling](#scaling)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Disaster Recovery](#disaster-recovery)

---

## Quick Start

### Prerequisites

- Docker & Docker Compose (for containerized deployment)
- Kubernetes cluster (for K8s deployment)
- AWS account with permissions (for AWS deployment)
- Stripe account for billing
- PostgreSQL 13+ (production database)

---

## Docker Deployment

### Build Docker Image

```bash
# Build API image
docker build -f backend/Dockerfile -t codeai:latest .

# Or use docker-compose for full stack
docker-compose up -d
```

### Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-api.txt requirements-monitoring.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-api.txt -r requirements-monitoring.txt

# Copy application code
COPY backend/ ./backend/
COPY sdk/ ./sdk/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "backend.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://codeai:password@db:5432/codeai
      - STRIPE_API_KEY=${STRIPE_API_KEY}
      - STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
      - MODEL_PATH=/models/starcode-7b
    volumes:
      - ./models:/models
      - ./backend/logs:/app/backend/logs
    depends_on:
      - db
    networks:
      - codeai-network
    restart: unless-stopped

  db:
    image: postgres:13-alpine
    environment:
      - POSTGRES_USER=codeai
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=codeai
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - codeai-network
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./backend/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    networks:
      - codeai-network
    restart: unless-stopped

volumes:
  postgres_data:
  prometheus_data:

networks:
  codeai-network:
    driver: bridge
```

**Run services:**
```bash
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop services
docker-compose down
```

---

## Kubernetes Deployment

### Helm Chart Structure

```
helm/codeai/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
```

### Deployment Manifest

Create `helm/codeai/templates/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "codeai.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: codeai
  template:
    metadata:
      labels:
        app: codeai
    spec:
      containers:
      - name: api
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: codeai-secrets
              key: database-url
        - name: STRIPE_API_KEY
          valueFrom:
            secretKeyRef:
              name: codeai-secrets
              key: stripe-api-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Service & Ingress

```yaml
apiVersion: v1
kind: Service
metadata:
  name: codeai-api
spec:
  selector:
    app: codeai
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: codeai-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: api.codeai.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: codeai-api
            port:
              number: 80
  tls:
  - hosts:
    - api.codeai.example.com
    secretName: codeai-tls
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: codeai-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: codeai
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Deploy to Kubernetes:**
```bash
# Create namespace
kubectl create namespace codeai

# Create secrets
kubectl create secret generic codeai-secrets \
  --from-literal=database-url=postgresql://... \
  --from-literal=stripe-api-key=sk_live_... \
  -n codeai

# Install Helm chart
helm install codeai helm/codeai/ -n codeai

# Verify deployment
kubectl get pods -n codeai
kubectl logs -f deployment/codeai -n codeai

# Get service endpoint
kubectl get svc -n codeai
```

---

## AWS Deployment

### Option 1: ECS Fargate

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name codeai-prod

# Create task definition (task-definition.json)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster codeai-prod \
  --service-name codeai-api \
  --task-definition codeai:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Option 2: EC2 with Auto Scaling

```bash
# Create launch template
aws ec2 create-launch-template \
  --launch-template-name codeai-template \
  --launch-template-data file://launch-template.json

# Create Auto Scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name codeai-asg \
  --launch-template LaunchTemplateName=codeai-template,Version='$Latest' \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 3 \
  --availability-zones us-east-1a us-east-1b us-east-1c
```

### RDS Database Setup

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier codeai-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username codeai_admin \
  --master-user-password "SecurePassword123!" \
  --allocated-storage 100 \
  --backup-retention-period 30 \
  --multi-az \
  --enable-cloudwatch-logs-exports postgresql
```

---

## Environment Configuration

### Required Environment Variables

```bash
# API Configuration
ENVIRONMENT=production
API_KEY_PREFIX=sk_live_
MODEL_PATH=/models/starcode-7b
INFERENCE_TIMEOUT_SECONDS=60

# Database
DATABASE_URL=postgresql://user:password@host:5432/codeai_prod
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Stripe Billing
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Monitoring
PROMETHEUS_ENABLED=true
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/codeai/api.log

# Security
ALLOWED_ORIGINS=https://codeai.example.com,https://editor.codeai.example.com
CORS_ALLOW_CREDENTIALS=true
TLS_CERT_PATH=/etc/certs/cert.pem
TLS_KEY_PATH=/etc/certs/key.pem

# Rate Limiting
DEFAULT_RATE_LIMIT_RPM=100
PREMIUM_RATE_LIMIT_RPM=600
ENTERPRISE_RATE_LIMIT_RPM=9999
```

### Secrets Management

**Using AWS Secrets Manager:**
```bash
# Store secrets
aws secretsmanager create-secret \
  --name codeai/prod/stripe-key \
  --secret-string 'sk_live_...'

# Retrieve in application
import boto3
secrets_client = boto3.client('secretsmanager')
secret = secrets_client.get_secret_value(SecretId='codeai/prod/stripe-key')
STRIPE_API_KEY = secret['SecretString']
```

---

## Monitoring & Observability

### Prometheus Setup

```yaml
# backend/monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'codeai-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

**Access Prometheus dashboard:** `http://localhost:9090`

### ELK Stack Integration (Elasticsearch + Logstash + Kibana)

```yaml
# docker-compose.yml addition
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./backend/monitoring/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
```

**Access Kibana:** `http://localhost:5601`

### CloudWatch Monitoring (AWS)

```python
import boto3
from backend.monitoring.prometheus_metrics import inference_latency_seconds

# Send custom metrics to CloudWatch
cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_data(
    Namespace='CodeAI/Production',
    MetricData=[
        {
            'MetricName': 'InferenceLatency',
            'Value': 145.3,
            'Unit': 'Milliseconds'
        }
    ]
)
```

---

## Scaling

### Horizontal Scaling

**Add more replicas:**
```bash
# Kubernetes
kubectl scale deployment codeai --replicas=5 -n codeai

# Docker Swarm
docker service scale codeai_api=5
```

### Vertical Scaling

**Increase resource limits in Kubernetes:**
```yaml
resources:
  requests:
    memory: "4Gi"
    cpu: "2000m"
  limits:
    memory: "8Gi"
    cpu: "4000m"
```

### Model Optimization

**Quantization for faster inference:**
```python
# Use int8 quantization
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "starcode-7b",
    load_in_8bit=True,  # Reduces memory by 4x, ~10-20% slower
    device_map="auto"
)
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run tests
        run: |
          pip install -r requirements-dev.txt
          pytest tests/ -v --cov
      
      - name: Check code quality
        run: |
          pylint backend/ --fail-under=8.0
          black --check backend/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t codeai:${{ github.sha }} .
      
      - name: Push to ECR
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          aws ecr get-login-password --region us-east-1 | \
            docker login --username AWS --password-stdin ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com
          docker tag codeai:${{ github.sha }} ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/codeai:${{ github.sha }}
          docker push ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/codeai:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          aws ecs update-service \
            --cluster codeai-prod \
            --service codeai-api \
            --force-new-deployment
      
      - name: Health check
        run: |
          sleep 30
          curl -f https://api.codeai.example.com/health || exit 1
```

---

## Disaster Recovery

### Backup Strategy

**Database backups:**
```bash
# Manual backup
pg_dump postgresql://user:pass@host/codeai > backup-$(date +%Y%m%d-%H%M%S).sql

# Automated backups (AWS RDS)
# RDS has automated backups with 30-day retention configured
aws rds describe-db-instances --db-instance-identifier codeai-db
```

**Model checkpoints:**
```bash
# Backup model files to S3
aws s3 cp /models/starcode-7b/ s3://codeai-backups/models/starcode-7b/ --recursive

# Restore from S3
aws s3 cp s3://codeai-backups/models/starcode-7b/ /models/starcode-7b/ --recursive
```

### Recovery Procedures

**Database Recovery:**
```bash
# Restore from backup
psql postgresql://user:pass@host/codeai < backup.sql

# Or use RDS restore-to-point-in-time
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier codeai-db \
  --target-db-instance-identifier codeai-db-recovered \
  --restore-time 2024-01-16T10:00:00Z
```

**Service Recovery:**
```bash
# Restart all pods in Kubernetes
kubectl rollout restart deployment codeai -n codeai

# Check rollout status
kubectl rollout status deployment codeai -n codeai
```

---

## Runbooks

### Incident: High Latency

1. Check Prometheus metrics: `rate(inference_latency_seconds[5m])`
2. Check GPU/CPU utilization: `node_cpu_usage`, `node_memory_usage`
3. If utilization high: Scale up replicas or add nodes
4. If utilization low: Check for slow database queries in logs
5. Restart API pods if necessary: `kubectl rollout restart deployment codeai`

### Incident: Out of Memory

1. Check memory usage: `kubectl top pods -n codeai`
2. Check model size: Is quantization enabled?
3. Reduce batch size or enable inference quantization
4. Increase pod memory limits
5. Restart affected pods

### Incident: Database Connection Pool Exhausted

1. Check active connections: `SELECT count(*) FROM pg_stat_activity;`
2. Increase `DB_POOL_SIZE` environment variable
3. Restart API pods: `kubectl rollout restart deployment codeai`
4. Monitor connection usage: `DB_POOL_SIZE` should be at 80% max

---

## Support

- **Documentation:** https://codeai.example.com/docs
- **Status Page:** https://status.codeai.example.com
- **Email:** ops@codeai.example.com
- **Slack:** #codeai-ops
