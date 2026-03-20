# bloque-notifications

Notification orchestrator with pluggable providers and template rendering.

## Features

- **Template rendering** - Jinja2 (optional) with `str.format_map()` fallback
- **Pluggable providers** - WebhookProvider, ConsoleProvider, or any duck-typed provider
- **Multi-channel routing** - Send one notification to multiple channels
- **Tenant-aware templates** - Automatic tenant prefix via bloque-multitenant context
- **Async by design** - All I/O operations are async

## Installation

```bash
uv add bloque-notifications

# With Jinja2 template support
uv add bloque-notifications[templates]
```

## Quick Start

```python
from bloque_notifications import NotificationService, ConsoleProvider, Notification, Channel

service = NotificationService(
    providers={Channel.CONSOLE: ConsoleProvider()},
)

await service.start()

# Simple notification (no template)
result = await service.notify_simple(
    recipient="admin@example.com",
    subject="Deploy complete",
    body="Version 2.1.0 deployed successfully.",
    channels=[Channel.CONSOLE],
)

# Template-based notification
service.template_engine.register(
    "welcome",
    subject="Welcome, {name}!",
    body="Hello {name}, your account on {app} is ready.",
)

result = await service.notify(Notification(
    recipient="user@example.com",
    template_name="welcome",
    context={"name": "Alice", "app": "MyApp"},
    channels=[Channel.CONSOLE],
))

await service.stop()
```

## Connecting bloque-channels as Email Provider

bloque-notifications does NOT depend on bloque-channels. You can connect
any object that satisfies the `NotificationProvider` protocol via duck-typing:

```python
from bloque_channels.email.client import EmailClient
from bloque_channels.models.settings import EmailSettings
from bloque_notifications import NotificationService, Channel
from bloque_notifications.protocol import NotificationProvider

class EmailAdapter:
    """Adapt EmailClient to NotificationProvider protocol."""

    def __init__(self, client: EmailClient) -> None:
        self._client = client

    async def send(self, recipient, subject, body, *, metadata=None):
        from bloque_channels.models.message import OutboundMessage
        msg = OutboundMessage(to=recipient, subject=subject, body=body)
        return await self._client.send_message(msg)

    async def health_check(self) -> bool:
        return await self._client.health_check()

# Usage
email = EmailClient(EmailSettings(host="smtp.example.com"))
service = NotificationService(
    providers={Channel.EMAIL: EmailAdapter(email)},
)
```

## Providers

| Provider | Channel | Description |
|----------|---------|-------------|
| `ConsoleProvider` | CONSOLE | Logs notifications via bloque-core logger |
| `WebhookProvider` | WEBHOOK | POSTs JSON payload to recipient URL |

## API

See source code docstrings for full API documentation.
