# Cloud Deployment Commands

## Local Docker Compose
```bash
docker compose up --build -d
```

## Initialize PostgreSQL schema
```bash
cat scripts/init_postgres.sql | docker compose exec -T postgres psql -U postgres -d appdb
```

## Stop services
```bash
docker compose down
```

## Example cloud deployment flow (generic)
```bash
# 1. Build image

docker build -t your-registry/ai-app:latest .

# 2. Push image

docker push your-registry/ai-app:latest

# 3. Deploy to your host or platform
# Example with a managed container platform:
# - create a PostgreSQL service
# - create a Redis service
# - set environment variables from .env.production
# - deploy the image
```
