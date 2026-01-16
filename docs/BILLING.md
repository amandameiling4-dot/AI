# Billing & Monetization

## Objective
Provide a flexible, secure monetization model for hosted usage while supporting local/free options for privacy-focused users.

## Pricing model (suggested)
- **Freemium**: free tier with limited monthly quota (e.g., 1000 tokens / 10k characters). Good for onboarding.
- **Pay-as-you-go**: per-token pricing for usage above free quota. Meter requests and bill monthly.
- **Subscriptions**: monthly/annual tiers for individuals and teams (seat-based or usage-included). Include priority support for higher tiers.
- **Enterprise**: custom on-prem licensing, volume discounts, SLA & dedicated support.

## Key components
- **Payment provider**: Stripe (recommended) for card payments, invoices, subscriptions.
- **Auth**: API keys & user accounts (OAuth or email/password). Clients (VS Code) will send API keys for hosted requests.
- **Metering**: track tokens & requests per user and reconcile to billing cycles.
- **Enforcement**: rate-limiting and quota checks at the API layer.

## Data model (high-level)
- Users (accounts)
- StripeCustomer (maps user to Stripe customer ID)
- Subscriptions (plan ID, status)
- UsageRecord (timestamp, user_id, tokens, request_id)
- Invoices (stripe invoice id, status)

## API surface (suggested endpoints)
- POST /billing/subscribe — start a subscription (creates Stripe Checkout / customer)
- POST /billing/usage — report usage (server-side metering)
- GET /billing/invoices — list invoices for user
- POST /billing/webhook — receive Stripe webhook events

## Webhook handling
Verify Stripe webhook signatures. Handle events: invoice.paid, invoice.payment_failed, customer.subscription.updated, checkout.session.completed.

## Security & compliance
- Use Stripe to minimize PCI scope
- Store minimal payment-related data
- Implement GDPR, privacy, and data retention policies
- Require secure storage for API keys and secrets (env or secret manager)

## Testing & monitoring
- Add unit tests for billing flows and webhook events
- Setup monitoring/alerting for failed invoices and webhook processing errors
- Add audit logs for billing actions

## Developer quick start
1. Add STRIPE_API_KEY and STRIPE_WEBHOOK_SECRET to environment
2. Start the billing service (see `backend/billing/README.md`)
3. Use test mode keys and Stripe CLI to send webhook events during local development

---

## Next steps (implementation tasks)
- Add server-side subscription endpoints and Stripe checkout flows
- Implement usage metering and billing reconciliation jobs
- Add user-facing billing dashboard and invoices UI
- Add tests and monitoring

(See `backend/billing` for skeleton code and examples.)