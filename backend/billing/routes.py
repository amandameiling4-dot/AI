from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel
import os
import stripe

stripe.api_key = os.getenv("STRIPE_API_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

app = FastAPI()

class SubscribeRequest(BaseModel):
    price_id: str
    customer_email: str


@app.post("/billing/subscribe")
async def subscribe(req: SubscribeRequest):
    # Create a Stripe Checkout session (or Subscription) for the customer
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": req.price_id, "quantity": 1}],
            mode="subscription",
            customer_email=req.customer_email,
            success_url="https://your-app.example.com/billing/success",
            cancel_url="https://your-app.example.com/billing/cancel",
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UsageRecord(BaseModel):
    user_id: str
    tokens: int
    request_id: str | None = None


@app.post("/billing/usage")
async def record_usage(u: UsageRecord):
    # Persist usage for billing reconciliation (stub)
    # TODO: validate user, persist to DB, return quota info
    return {"status": "ok", "billed_tokens": u.tokens}


@app.post("/billing/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    # Handle webhook events
    if event.type == "invoice.paid":
        invoice = event.data.object
        # TODO: mark invoice as paid in DB
    elif event.type == "invoice.payment_failed":
        invoice = event.data.object
        # TODO: notify user, update subscription status
    elif event.type == "checkout.session.completed":
        session = event.data.object
        # TODO: create a subscription record for user

    return {"status": "processed"}
