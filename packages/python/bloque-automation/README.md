# bloque-automation

Rule engine with composable condition evaluator and pluggable action handlers.

## Features

- **Condition tree**: AND/OR/NOT logic + comparison operators (eq, gt, in, regex, etc.)
- **Sync evaluator**: Pure function, no I/O, fully testable
- **Pluggable handlers**: ActionHandler protocol - bring your own action implementations
- **Tenant-aware**: Optional multitenant isolation via bloque-multitenant context
- **Error-resilient**: Missing fields return False, failed actions don't crash the engine

## Install

```bash
uv add bloque-automation
```

## Quick Start

```python
from bloque_automation import (
    Action, ActionType, Condition, LogActionHandler,
    Operator, Rule, RuleEngine,
)

# Define a condition: user.age >= 18
condition = Condition(operator=Operator.GTE, field="user.age", value=18)

# Define a rule with a log action
rule = Rule(
    rule_id="adult-check",
    name="Adult User Check",
    conditions=condition,
    actions=[Action(action_type=ActionType.LOG, name="log-adult")],
)

# Create engine and register handler
engine = RuleEngine()
engine.register_handler(ActionType.LOG, LogActionHandler())
engine.add_rule(rule)

# Evaluate an event
async with engine:
    results = await engine.evaluate({"user": {"age": 25}})
    assert results[0].matched is True
```

## Condition Operators

### Comparison
| Operator | Description |
|----------|-------------|
| `eq` | Equal |
| `neq` | Not equal |
| `gt` | Greater than |
| `gte` | Greater than or equal |
| `lt` | Less than |
| `lte` | Less than or equal |
| `in` | Value in list |
| `not_in` | Value not in list |
| `contains` | String contains |
| `starts_with` | String starts with |
| `ends_with` | String ends with |
| `regex` | Regex match |

### Logical
| Operator | Description |
|----------|-------------|
| `and` | All children must match |
| `or` | Any child must match |
| `not` | Invert single child |

## Nested Fields

Use dot-path notation to access nested dict keys:

```python
condition = Condition(operator=Operator.EQ, field="user.plan.tier", value="premium")
event = {"user": {"plan": {"tier": "premium"}}}
# evaluates to True
```

## Custom Action Handler

Implement the `ActionHandler` protocol:

```python
class NotificationActionHandler:
    def __init__(self, notification_service):
        self.service = notification_service

    async def execute(self, action, context):
        await self.service.notify_simple(
            action.config["recipient"],
            action.config["subject"],
            str(context),
        )
        return {"status": "sent"}

    async def health_check(self):
        return True

engine.register_handler(ActionType.NOTIFY, NotificationActionHandler(svc))
```

## Dependencies

Only `bloque-core`. Handlers that need HTTP, notifications, etc. bring their own deps.
