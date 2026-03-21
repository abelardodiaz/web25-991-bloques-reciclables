# ulfblk-channels

Webhook handlers para WhatsApp (Meta Cloud API), Telegram (Bot API), y Email (inbound webhook + SMTP outbound).

## Instalacion

```bash
uv add ulfblk-channels
```

Para email outbound (SMTP):

```bash
uv add ulfblk-channels[email]
```

## WhatsApp

```python
from fastapi import FastAPI
from bloque_channels.whatsapp import WhatsAppRouter, WhatsAppSettings

app = FastAPI()

settings = WhatsAppSettings(
    api_token="tu-token",
    verify_token="mi-token-verificacion",
    phone_number_id="123456789",
)

whatsapp = WhatsAppRouter(
    verify_token=settings.verify_token,
    on_message=lambda msg: print(f"Mensaje: {msg.text}"),
    settings=settings,
)

app.include_router(whatsapp.router, prefix="/webhook")
```

## Telegram

```python
from bloque_channels.telegram import TelegramRouter, TelegramSettings

settings = TelegramSettings(
    bot_token="123:ABC",
    secret_token="mi-secret",
)

telegram = TelegramRouter(
    on_message=lambda msg: print(f"Mensaje: {msg.text}"),
    settings=settings,
    secret_token=settings.secret_token,
)

app.include_router(telegram.router, prefix="/telegram")
```

## Email

```python
from bloque_channels.email import EmailRouter, EmailClient, EmailSettings

# Inbound (webhook)
email_router = EmailRouter(
    on_message=lambda msg: print(f"Email de: {msg.sender}"),
    webhook_secret="secret",
)
app.include_router(email_router.router, prefix="/email")

# Outbound (SMTP, requiere ulfblk-channels[email])
email_settings = EmailSettings(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_username="user@gmail.com",
    smtp_password="app-password",
    from_address="user@gmail.com",
)
client = EmailClient(email_settings)
await client.send_text("dest@example.com", "Asunto", "Cuerpo del email")
```

## Health Check

```python
from bloque_channels.health import channels_health_check
from bloque_channels.whatsapp import WhatsAppClient
from bloque_channels.telegram import TelegramClient

channels = {
    "whatsapp": whatsapp_client,
    "telegram": telegram_client,
}
status = await channels_health_check(channels)
# {"whatsapp": True, "telegram": False}
```

## Dependencias

- `ulfblk-core` (obligatorio)
- `httpx>=0.27` (obligatorio)
- `aiosmtplib>=3.0` (opcional, para email outbound)

## License

MIT
