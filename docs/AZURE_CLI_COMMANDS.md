# Azure CLI commands for Azure Container Apps

This guide targets one specific deployment setup:
- Azure Container Apps
- Azure Container Registry
- Azure Database for PostgreSQL Flexible Server
- Azure Cache for Redis

## Current repo status

The codebase is healthy from the local verification run:
- Editor diagnostics: no errors found
- Test suite: 29 passed, 1 non-blocking warning

The only deployment-specific caution is that PostgreSQL and Redis connections should use TLS-enabled connection strings in Azure.

## 1. Login and register providers

```bash
az login

az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Cache
```

## 2. Create shared resources

```bash
export RESOURCE_GROUP=ai-rg
export LOCATION=eastus
export ACR_NAME=aiacr$(openssl rand -hex 3)
export CONTAINER_ENV=ai-env
export CONTAINER_APP=ai-api
export POSTGRES_SERVER=ai-postgres-$(openssl rand -hex 3)
export POSTGRES_ADMIN_USER=postgres
export POSTGRES_ADMIN_PASSWORD='ChangeMe123!'
export POSTGRES_DB=appdb
export REDIS_NAME=ai-redis-$(openssl rand -hex 3)
export REDIS_SKU=Basic
export REDIS_SIZE=C0
export JWT_SECRET_KEY='replace-with-long-random-secret'
export API_TOKEN='replace-with-api-token'

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
```

## 3. Create Azure Container Registry

```bash
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Basic \
  --admin-enabled true
```

## 4. Create Azure Database for PostgreSQL Flexible Server

```bash
az postgres flexible-server create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$POSTGRES_SERVER" \
  --location "$LOCATION" \
  --admin-user "$POSTGRES_ADMIN_USER" \
  --admin-password "$POSTGRES_ADMIN_PASSWORD" \
  --sku-name Standard_B1ms \
  --version 16 \
  --storage-size 32 \
  --public-access 0.0.0.0 \
  --database-name "$POSTGRES_DB"

POSTGRES_HOST=$(az postgres flexible-server show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$POSTGRES_SERVER" \
  --query fullyQualifiedDomainName -o tsv)
```

## 5. Create Azure Cache for Redis

```bash
az redis create \
  --name "$REDIS_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku "$REDIS_SKU" \
  --vm-size "$REDIS_SIZE"

REDIS_HOST=$(az redis show \
  --name "$REDIS_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query hostName -o tsv)

REDIS_KEY=$(az redis list-keys \
  --name "$REDIS_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query primaryKey -o tsv)
```

## 6. Build and push the container image

```bash
az acr login --name "$ACR_NAME"
az acr build --registry "$ACR_NAME" --image ai-app:latest .
```

## 7. Create the Container Apps environment

```bash
az containerapp env create \
  --name "$CONTAINER_ENV" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION"
```

## 8. Create the app and wire secrets

```bash
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query passwords[0].value -o tsv)

az containerapp create \
  --name "$CONTAINER_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$CONTAINER_ENV" \
  --image "$ACR_NAME.azurecr.io/ai-app:latest" \
  --target-port 8000 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 1 \
  --max-replicas 1 \
  --registry-server "$ACR_NAME.azurecr.io" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD" \
  --env-vars \
    DATABASE_URL="postgresql://$POSTGRES_ADMIN_USER:$POSTGRES_ADMIN_PASSWORD@$POSTGRES_HOST:5432/$POSTGRES_DB?sslmode=require" \
    JWT_SECRET_KEY="$JWT_SECRET_KEY" \
    API_TOKEN="$API_TOKEN" \
    REDIS_URL="rediss://:$REDIS_KEY@$REDIS_HOST:6380"
```

## 9. Update the app later

```bash
az containerapp update \
  --name "$CONTAINER_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --image "$ACR_NAME.azurecr.io/ai-app:latest"
```

## 10. Useful follow-up checks

```bash
az containerapp show --name "$CONTAINER_APP" --resource-group "$RESOURCE_GROUP" --query properties.configuration.ingress.fqdn -o tsv
az containerapp logs show --name "$CONTAINER_APP" --resource-group "$RESOURCE_GROUP" --follow
```

## Notes

- Replace the secret values before deployment.
- If you use a stricter firewall policy, allow inbound access to the PostgreSQL and Redis endpoints from the Container Apps environment.
- The locally verified app health is good; the remaining deployment risk is cloud networking and secret configuration rather than code errors.
