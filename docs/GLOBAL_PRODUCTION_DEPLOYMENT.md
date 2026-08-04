# Global Production Deployment Guide

## 1. Target architecture
- API service behind a load balancer
- PostgreSQL managed database
- Redis managed cache
- object storage for assets and uploads
- CDN for global static content
- monitoring and alerting

## 2. Recommended host options
- Render
- Railway
- Fly.io
- Azure App Service
- DigitalOcean App Platform
- AWS Elastic Beanstalk / ECS

## 3. Deployment pipeline
1. Build container image from the existing Dockerfile.
2. Push image to a container registry.
3. Create environment variables from .env.production.
4. Deploy API service with health checks.
5. Run PostgreSQL initialization SQL.
6. Enable autoscaling and monitoring.

## 4. Example commands
```bash
docker build -t your-registry/ai-app:latest .
docker push your-registry/ai-app:latest
```

## 5. Production checklist
- HTTPS enabled
- secrets stored securely
- database backups enabled
- Redis and Postgres connectivity verified
- monitoring and alerts configured
- rollback plan documented
