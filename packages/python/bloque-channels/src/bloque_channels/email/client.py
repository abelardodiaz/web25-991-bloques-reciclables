"""Email client for sending messages via SMTP (optional dep: aiosmtplib)."""

from __future__ import annotations

from email.message import EmailMessage
from typing import Any

from bloque_channels.models.message import OutboundMessage
from bloque_channels.models.settings import EmailSettings


class EmailClient:
    """Send emails via SMTP using aiosmtplib.

    Requires ``pip install bloque-channels[email]`` for aiosmtplib.

    Example:
        client = EmailClient(settings)
        await client.send_text("dest@example.com", "Asunto", "Cuerpo")
    """

    def __init__(self, settings: EmailSettings) -> None:
        self.settings = settings

    async def send_text(self, to: str, subject: str, body: str) -> None:
        """Send a plain-text email.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            body: Plain-text email body.

        Raises:
            ImportError: If aiosmtplib is not installed.
        """
        try:
            import aiosmtplib
        except ImportError as exc:
            raise ImportError(
                "aiosmtplib is required for email sending. "
                "Install with: pip install bloque-channels[email]"
            ) from exc

        msg = EmailMessage()
        msg["From"] = self.settings.from_address
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        await aiosmtplib.send(
            msg,
            hostname=self.settings.smtp_host,
            port=self.settings.smtp_port,
            username=self.settings.smtp_username or None,
            password=self.settings.smtp_password or None,
            use_tls=self.settings.smtp_use_tls,
        )

    async def send_message(self, message: OutboundMessage) -> dict[str, Any]:
        """Send a message using the ChannelProtocol interface."""
        subject = message.metadata.get("subject", "Message")
        await self.send_text(message.recipient, subject, message.text)
        return {"status": "sent", "to": message.recipient}

    async def health_check(self) -> bool:
        """Check if the SMTP server is reachable.

        Returns False if aiosmtplib is not installed.
        """
        try:
            import aiosmtplib

            smtp = aiosmtplib.SMTP(
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
                use_tls=self.settings.smtp_use_tls,
            )
            await smtp.connect()
            await smtp.quit()
            return True
        except ImportError:
            return False
        except Exception:
            return False
