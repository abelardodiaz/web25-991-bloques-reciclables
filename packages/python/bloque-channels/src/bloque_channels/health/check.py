"""Aggregate health check across multiple channels."""

from __future__ import annotations

from bloque_channels.protocol.channel import ChannelProtocol


async def channels_health_check(
    channels: dict[str, ChannelProtocol],
) -> dict[str, bool]:
    """Run health checks on all registered channels.

    Args:
        channels: Mapping of channel name to client instance.

    Returns:
        Dict with channel names and their health status.

    Example:
        status = await channels_health_check({
            "whatsapp": wa_client,
            "telegram": tg_client,
        })
        # {"whatsapp": True, "telegram": False}
    """
    results: dict[str, bool] = {}
    for name, channel in channels.items():
        try:
            results[name] = await channel.health_check()
        except Exception:
            results[name] = False
    return results
