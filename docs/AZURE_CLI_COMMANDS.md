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

## Secret setup in Azure (step by step)

### Option A: Set secrets with Azure CLI

1. Create strong values for each secret locally, but avoid echoing them into shell history.

```bash
export JWT_SECRET_KEY='replace-with-long-random-secret'
export API_TOKEN='replace-with-api-token'
export POSTGRES_PASSWORD='ChangeMe123!'
export REDIS_KEY='replace-with-redis-key'
```

2. Store them as Container Apps secrets.

```bash
az containerapp secret set \
  --name "$CONTAINER_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --secrets \
    jwt-secret="$JWT_SECRET_KEY" \
    api-token="$API_TOKEN" \
    postgres-password="$POSTGRES_PASSWORD" \
    redis-key="$REDIS_KEY"
```

3. Attach those secrets to the app environment variables.

```bash
az containerapp update \
  --name "$CONTAINER_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --set-env-vars \
    JWT_SECRET_KEY=secretref:jwt-secret \
    API_TOKEN=secretref:api-token \
    DATABASE_URL="postgresql://postgres:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432/$POSTGRES_DB?sslmode=require" \
    REDIS_URL="rediss://:$REDIS_KEY@$REDIS_HOST:6380"
```

4. Verify the app has the expected values.

```bash
az containerapp show \
  --name "$CONTAINER_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --query "properties.template.containers[0].env" -o json
```

### Option B: Set secrets in the Azure portal

1. Open the Azure portal and go to your Container App.
2. Open the "Secrets" blade.
3. Click "Add" and create a secret name such as `jwt-secret`.
4. Paste the secret value and save it.
5. Open "Containers" > your container > "Environment variables".
6. Add each variable and select the corresponding secret reference.
7. Save and restart the container app.

> Avoid storing secrets directly in source code, Dockerfiles, or plain shell history. Prefer Azure Container Apps secrets or Azure Key Vault.

## TLS-enabled connection strings

### PostgreSQL (Azure Database for PostgreSQL Flexible Server)

Use the fully qualified server hostname and require TLS.

```bash
export POSTGRES_HOST="<your-postgres-server>.postgres.database.azure.com"
export POSTGRES_DB="appdb"
export POSTGRES_ADMIN_USER="postgres"
export POSTGRES_ADMIN_PASSWORD='ChangeMe123!'
```

Example connection string:

```bash
DATABASE_URL="postgresql://$POSTGRES_ADMIN_USER:$POSTGRES_ADMIN_PASSWORD@$POSTGRES_HOST:5432/$POSTGRES_DB?sslmode=require"
```

Important notes:
- The host must be the Azure PostgreSQL server FQDN, not `localhost`.
- Use `sslmode=require` so the client negotiates TLS.
- If your app uses SQLAlchemy, the URL can also be written as `postgresql+psycopg2://...` depending on the driver you installed.

### Redis (Azure Cache for Redis)

Azure Cache for Redis requires TLS. Use the `rediss://` scheme and port `6380`.

```bash
export REDIS_HOST="<your-redis-name>.redis.cache.windows.net"
export REDIS_KEY='replace-with-redis-key'
```

Example connection string:

```bash
REDIS_URL="rediss://:$REDIS_KEY@$REDIS_HOST:6380"
```

Important notes:
- Use `rediss://` instead of `redis://`.
- Use port `6380` for TLS.
- If your Redis client requires a username, add it before the password in the URL form.

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

## GitHub Actions deployment setup

This project includes a ready-to-run Azure deployment workflow at `.github/workflows/deploy-azure.yml`.

### Required repository secrets

Set these secrets in GitHub repo Settings > Secrets > Actions:
- `AZURE_CREDENTIALS`: the JSON output from `az ad sp create-for-rbac ... --sdk-auth`
- `ACR_NAME`: the Azure Container Registry name (e.g. `aiacr123`)
- `AZURE_RESOURCE_GROUP`: the resource group name
- `AZURE_LOCATION`: the Azure region (for example `eastus`)
- `AZURE_CONTAINER_ENV`: the Container Apps environment name
- `AZURE_CONTAINER_APP`: the Container App name
- `DATABASE_URL`: TLS-enabled PostgreSQL string, for example:
  `postgresql://postgres:<password>@<server>.postgres.database.azure.com:5432/appdb?sslmode=require`
- `JWT_SECRET_KEY`: your production JWT secret
- `API_TOKEN`: your API bearer token
- `REDIS_URL`: TLS-enabled Redis string, for example:
  `rediss://:<key>@<server>.redis.cache.windows.net:6380`

### Exact commands to create the service principal and secrets

```bash
# Authenticate to Azure and choose the subscription
az login
az account list --all -o table
az account set --subscription "<SUBSCRIPTION_ID>"

# Create a service principal with Contributor access to the subscription
az ad sp create-for-rbac \
  --name "ai-app-sp" \
  --role "Contributor" \
  --scopes "/subscriptions/<SUBSCRIPTION_ID>" \
  --sdk-auth > azure-credentials.json

# Store the credentials as a GitHub Actions secret
cat azure-credentials.json | gh secret set AZURE_CREDENTIALS --repo amandameiling4-dot/AI --body -

# Store the ACR name as a GitHub Actions secret
gh secret set ACR_NAME --repo amandameiling4-dot/AI --body "<your-acr-name>"
```

### Exact commands to provision Azure resources manually

```bash
export RESOURCE_GROUP=ai-rg
export LOCATION=eastus
export ACR_NAME=<your-acr-name>
export CONTAINER_ENV=ai-env
export CONTAINER_APP=ai-api
export POSTGRES_SERVER=<your-postgres-server>
export POSTGRES_DB=appdb
export POSTGRES_ADMIN_USER=postgres
export POSTGRES_ADMIN_PASSWORD='<your-password>'
export REDIS_NAME=<your-redis-name>
export REDIS_KEY='<your-redis-key>'

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Basic \
  --admin-enabled true

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

az redis create \
  --name "$REDIS_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Basic \
  --vm-size C0
```

### Exact commands to run the GitHub Actions workflow

After adding the secrets and pushing the branch, trigger the workflow by pushing to `main` or using the `workflow_dispatch` button in GitHub Actions.

If you want to deploy manually from the CLI instead, use:

```bash
az acr login --name "$ACR_NAME"
az acr build --registry "$ACR_NAME" --image ai-app:latest .

az containerapp env create \
  --name "$CONTAINER_ENV" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION"

az containerapp create \
  --name "$CONTAINER_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$CONTAINER_ENV" \
  --image "$ACR_NAME.azurecr.io/ai-app:latest" \
  --target-port 8000 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --registry-server "$ACR_NAME.azurecr.io" \
  --registry-username "<acr-username>" \
  --registry-password "<acr-password>" \
  --env-vars \
    DATABASE_URL="${DATABASE_URL}" \
    JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
    API_TOKEN="${API_TOKEN}" \
    REDIS_URL="${REDIS_URL}"
```

### Important note

This GitHub Actions workflow only deploys the container app and requires the Azure resources to already exist or to be provisioned separately. If your Azure account currently has no subscription, you must first enable a subscription before this workflow can apply the deployment.
