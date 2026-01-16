import os
import stripe
from sqlalchemy.orm import Session

stripe.api_key = os.getenv("STRIPE_API_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


def handle_event(event, db: Session = None):
    typ = event['type']
    data = event['data']['object']

    if typ == 'invoice.paid':
        # persist invoice paid status
        invoice_id = data.get('id')
        # TODO: update DB record
    elif typ == 'invoice.payment_failed':
        # handle failed payment
        # TODO: send notification
        pass
    elif typ == 'checkout.session.completed':
        # finalize subscription creation
        customer_email = data.get('customer_email')
        # TODO: map to user and persist subscription
    # Add more event handlers as needed

    return True