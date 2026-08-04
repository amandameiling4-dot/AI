# Azure deployment guide

## 1. Prerequisites
- Azure CLI installed and logged in
- An Azure Container Registry (ACR)
- An Azure App Service plan or Azure Container Apps environment
- A PostgreSQL flexible server and Azure Cache for Redis

## 2. Build and push image
```bash
az acr build --registry <acr-name> --image ai-app:latest .
```

## 3. Create App Service or Container Apps
### Option A: Azure App Service
```bash
az webapp create --resource-group <rg> --plan <plan> --name <app-name> --deployment-container-image-name <acr-name>.azurecr.io/ai-app:latest
```

### Option B: Azure Container Apps
```bash
az containerapp create --name <app-name> --resource-group <rg> --environment <env> --image <acr-name>.azurecr.io/ai-app:latest --target-port 8000 --ingress external
```

## 4. Environment variables
Set these in Azure:
- DATABASE_URL
- JWT_SECRET_KEY
- API_TOKEN
- STRIPE_API_KEY
- STRIPE_WEBHOOK_SECRET
- REDIS_URL

## 5. Health check
```bash
curl https://<app-name>.<region>.azurecontainerapps.io/health
```
