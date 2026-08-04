from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel
import os
from typing import Optional

try:
    import stripe
except ImportError:  # pragma: no cover - local fallback
    stripe = None

if stripe is not None:
    stripe.api_key = os.getenv("STRIPE_API_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

app = FastAPI()

class SubscribeRequest(BaseModel):
    price_id: str
    customer_email: str
    success_url: str = "https://api.codeai.app/billing/success"
    cancel_url: str = "https://api.codeai.app/billing/cancel"


class PaymentReceipt(BaseModel):
    receipt_id: str
    amount: float
    currency: str
    status: str
    paid_at: str
    customer_email: str


class PaymentWorkflowResponse(BaseModel):
    checkout_url: str
    session_id: str
    receipt: Optional[PaymentReceipt] = None


class PaymentStatusRequest(BaseModel):
    session_id: str
    payment_status: str
    receipt_id: Optional[str] = None


class PaymentStatusResponse(BaseModel):
    status: str
    message: str
    receipt: Optional[PaymentReceipt] = None


@app.post("/billing/subscribe", response_model=PaymentWorkflowResponse)
async def subscribe(req: SubscribeRequest):
    # Create a Stripe Checkout session (or Subscription) for the customer
    try:
        if stripe is None:
            session = type("Session", (), {"url": "https://example.com/checkout", "id": "local_session_123"})()
        else:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": req.price_id, "quantity": 1}],
                mode="subscription",
                customer_email=req.customer_email,
                success_url=req.success_url,
                cancel_url=req.cancel_url,
            )
        receipt = PaymentReceipt(
            receipt_id=f"rcpt_{session.id}",
            amount=0.0,
            currency="usd",
            status="pending",
            paid_at="",
            customer_email=req.customer_email,
        )
        return PaymentWorkflowResponse(checkout_url=session.url, session_id=session.id, receipt=receipt)
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


@app.post("/billing/payment-status", response_model=PaymentStatusResponse)
async def payment_status(req: PaymentStatusRequest):
    """Record payment status after checkout confirmation or manual payment updates."""
    receipt = PaymentReceipt(
        receipt_id=req.receipt_id or f"manual_{req.session_id}",
        amount=0.0,
        currency="usd",
        status=req.payment_status,
        paid_at="",
        customer_email="",
    )
    return PaymentStatusResponse(status=req.payment_status, message="Payment status recorded", receipt=receipt)


@app.post("/billing/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if stripe is None:
        return {"status": "processed", "event": "local-test", "payment_status": "received"}

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    # Handle webhook events
    if event.type == "invoice.paid":
        invoice = event.data.object
        return {
            "status": "processed",
            "event": event.type,
            "receipt_id": f"inv_{invoice.id}",
            "payment_status": "paid",
        }
    elif event.type == "invoice.payment_failed":
        invoice = event.data.object
        return {
            "status": "processed",
            "event": event.type,
            "receipt_id": f"inv_{invoice.id}",
            "payment_status": "failed",
        }
    elif event.type == "checkout.session.completed":
        session = event.data.object
        return {
            "status": "processed",
            "event": event.type,
            "receipt_id": f"sess_{session.id}",
            "payment_status": "completed",
        }

    return {"status": "processed", "event": event.type, "payment_status": "received"}
