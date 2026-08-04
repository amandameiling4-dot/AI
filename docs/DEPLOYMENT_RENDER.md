# Render deployment guide

## 1. Prerequisites
- A Render account
- A GitHub repository connected to Render
- PostgreSQL and Redis add-ons on Render

## 2. Environment variables
Set these in Render:
- DATABASE_URL
- JWT_SECRET_KEY
- API_TOKEN
- STRIPE_API_KEY
- STRIPE_WEBHOOK_SECRET
- REDIS_URL

## 3. Build and start command
Use the following start command:
```bash
uvicorn backend.api.server:app --host 0.0.0.0 --port 10000
```

## 4. Docker build
Render can also build from the Dockerfile:
```bash
docker build -t ai-app .
```

## 5. Deploy steps
1. Create a new Web Service in Render.
2. Connect the GitHub repo.
3. Choose Docker or the Python runtime.
4. Set the build/start commands.
5. Add the environment variables above.
6. Deploy.
