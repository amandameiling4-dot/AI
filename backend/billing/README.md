Billing backend (FastAPI) — quick start

Requirements:
- Python 3.10+
- Install: `pip install fastapi uvicorn stripe sqlalchemy alembic pydantic`

Environment:
- Set `STRIPE_API_KEY` and `STRIPE_WEBHOOK_SECRET` (see .env.example)

Run locally with:

```bash
uvicorn backend.billing.routes:app --reload --port 8001
```

Use Stripe CLI to forward webhooks during development:

```bash
stripe listen --forward-to localhost:8001/billing/webhook
```

This folder contains basic route handlers, webhook verification, and example DB models. It's a scaffold for integrating real billing flows.