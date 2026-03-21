"""Action model for rule execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ActionType(StrEnum):
    """Built-in action types.

    CUSTOM allows arbitrary handler registration.
    """

    NOTIFY = "notify"
    WEBHOOK = "webhook"
    LOG = "log"
    CUSTOM = "custom"


@dataclass
class Action:
    """An action to execute when a rule matches.

    Args:
        action_type: Type of action (determines which handler runs).
        config: Handler-specific configuration.
        name: Optional human-readable name for logging.
    """

    action_type: ActionType
    config: dict[str, Any] = field(default_factory=dict)
    name: str = ""
