# bloque-billing

Stripe billing integration: customers, subscriptions, checkout sessions, and webhooks.

## Features

- **Protocol-first**: BillingProvider protocol allows swapping Stripe for Paddle, LemonSqueezy, etc.
- **httpx client**: No Stripe SDK dependency - direct REST API calls with form-encoded bodies
- **Webhook verification**: HMAC-SHA256 signature validation using stdlib (no external deps)
- **Tenant-aware**: Optional multitenant isolation via metadata injection
- **Lifecycle managed**: async context manager with start/stop for httpx client

## Install

```bash
uv add bloque-billing
```

## Quick Start

```python
from bloque_billing import (
    BillingService, BillingSettings, CustomerCreate,
    CheckoutCreate, CheckoutMode, StripeProvider,
)

settings = BillingSettings(
    api_key="sk_test_...",
    webhook_secret="whsec_...",
)

provider = StripeProvider(settings)
service = BillingService(provider, settings=settings)

async with service:
    # Create a customer
    customer = await service.create_customer(
        CustomerCreate(email="user@example.com", name="Jane Doe")
    )

    # Create a checkout session
    checkout = await service.create_checkout_session(
        CheckoutCreate(
            customer_id=customer.id,
            price_id="price_xxx",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            mode=CheckoutMode.SUBSCRIPTION,
        )
    )
    print(checkout.url)  # redirect user here
```

## Webhook Processing

```python
from bloque_billing import WebhookProcessor, WebhookEventType

processor = WebhookProcessor(webhook_secret="whsec_...")

@processor.on(WebhookEventType.SUBSCRIPTION_CREATED)
async def handle_sub(event):
    print(f"New subscription: {event.data}")

# In your webhook endpoint:
event = await processor.process(payload=body, signature_header=sig)
```

## Custom Provider

Implement the `BillingProvider` protocol for any payment platform:

```python
from bloque_billing.protocol import BillingProvider

class PaddleProvider:
    async def create_customer(self, data):
        ...  # Paddle API calls

    async def health_check(self) -> bool:
        return True

    # ... implement all protocol methods
```

## Dependencies

Only `bloque-core` and `httpx`. Webhook verification uses stdlib `hmac`.
