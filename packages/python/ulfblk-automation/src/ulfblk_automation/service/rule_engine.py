"""Rule engine orchestrator."""

from __future__ import annotations

import logging
from typing import Any

from ulfblk_automation.evaluator.engine import evaluate_condition
from ulfblk_automation.models.action import Action
from ulfblk_automation.models.result import ActionResult, ActionStatus, RuleResult
from ulfblk_automation.models.rule import Rule
from ulfblk_automation.models.settings import RuleEngineSettings

logger = logging.getLogger(__name__)


class RuleEngine:
    """Orchestrate rule evaluation and action execution.

    Evaluates rules sorted by priority (descending), executes actions
    via registered handlers, and collects results.

    Args:
        settings: Engine configuration.

    Example:
        engine = RuleEngine()
        engine.register_handler(ActionType.LOG, LogActionHandler())
        engine.add_rule(rule)
        async with engine:
            results = await engine.evaluate({"user": {"age": 25}})
    """

    def __init__(self, *, settings: RuleEngineSettings | None = None) -> None:
        self.settings = settings or RuleEngineSettings()
        self._rules: dict[str, Rule] = {}
        self._handlers: dict[str, Any] = {}

    async def start(self) -> None:
        """Start the engine. Calls start() on handlers that have it."""
        for handler in self._handlers.values():
            if hasattr(handler, "start"):
                await handler.start()

    async def stop(self) -> None:
        """Stop the engine. Calls stop() on handlers that have it."""
        for handler in self._handlers.values():
            if hasattr(handler, "stop"):
                await handler.stop()

    def register_handler(self, action_type: str, handler: Any) -> None:
        """Register a handler for an action type.

        Args:
            action_type: The action type string (e.g. ActionType.LOG).
            handler: Object satisfying ActionHandler protocol.
        """
        self._handlers[str(action_type)] = handler

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the engine.

        Args:
            rule: The rule to add.

        Raises:
            ValueError: If max_rules limit is reached.
        """
        max_rules = self.settings.max_rules
        if max_rules > 0 and len(self._rules) >= max_rules:
            raise ValueError(
                f"Max rules limit reached ({max_rules})"
            )
        self._rules[rule.rule_id] = rule

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID.

        Returns:
            True if the rule was found and removed, False otherwise.
        """
        return self._rules.pop(rule_id, None) is not None

    def get_rules(
        self, *, tenant_id: str | None = None, enabled_only: bool = True
    ) -> list[Rule]:
        """Get rules, optionally filtered by tenant and enabled status.

        Args:
            tenant_id: Filter by tenant. None returns rules with no tenant.
            enabled_only: If True, only return enabled rules.

        Returns:
            List of matching rules sorted by priority descending.
        """
        rules = list(self._rules.values())

        if enabled_only:
            rules = [r for r in rules if r.enabled]

        if tenant_id is not None:
            rules = [r for r in rules if r.tenant_id == tenant_id or r.tenant_id is None]

        rules.sort(key=lambda r: r.priority, reverse=True)
        return rules

    async def evaluate(
        self, event: dict[str, Any], *, tenant_id: str | None = None
    ) -> list[RuleResult]:
        """Evaluate all matching rules against an event.

        Flow:
            1. Resolve tenant (explicit > multitenant context > None)
            2. Filter rules (tenant + enabled, sort by priority desc)
            3. Evaluate conditions per rule
            4. Execute actions for matching rules
            5. Collect results

        Args:
            event: The event data to evaluate.
            tenant_id: Explicit tenant override.

        Returns:
            List of RuleResult for each evaluated rule.
        """
        effective_tenant = tenant_id
        if effective_tenant is None and self.settings.tenant_aware:
            effective_tenant = self._resolve_tenant()

        rules = self.get_rules(tenant_id=effective_tenant, enabled_only=True)
        results: list[RuleResult] = []

        for rule in rules:
            try:
                matched = evaluate_condition(rule.conditions, event)
            except Exception as exc:
                logger.error("Error evaluating rule %s: %s", rule.rule_id, exc)
                results.append(
                    RuleResult(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        matched=False,
                        error=str(exc),
                    )
                )
                if self.settings.stop_on_rule_error:
                    break
                continue

            if not matched:
                results.append(
                    RuleResult(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        matched=False,
                    )
                )
                continue

            action_results = await self._execute_actions(rule.actions, event, rule)
            results.append(
                RuleResult(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    matched=True,
                    actions=action_results,
                )
            )

        return results

    async def _execute_actions(
        self, actions: list[Action], context: dict[str, Any], rule: Rule
    ) -> list[ActionResult]:
        """Execute actions sequentially, collecting results."""
        results: list[ActionResult] = []
        stopped = False

        for action in actions:
            if stopped:
                results.append(
                    ActionResult(
                        action_type=action.action_type,
                        status=ActionStatus.SKIPPED,
                        error="Skipped due to prior action failure",
                    )
                )
                continue

            handler = self._handlers.get(str(action.action_type))
            if handler is None:
                results.append(
                    ActionResult(
                        action_type=action.action_type,
                        status=ActionStatus.SKIPPED,
                        error=f"No handler registered for {action.action_type!r}",
                    )
                )
                continue

            try:
                detail = await handler.execute(action, context)
                results.append(
                    ActionResult(
                        action_type=action.action_type,
                        status=ActionStatus.SUCCESS,
                        detail=detail or {},
                    )
                )
            except Exception as exc:
                logger.error(
                    "Action %s failed: %s",
                    action.name or action.action_type,
                    exc,
                    exc_info=True,
                )
                results.append(
                    ActionResult(
                        action_type=action.action_type,
                        status=ActionStatus.FAILED,
                        error=str(exc),
                    )
                )
                if rule.stop_on_first_action_failure:
                    stopped = True

        return results

    @staticmethod
    def _resolve_tenant() -> str | None:
        """Try to read tenant from ulfblk_multitenant context."""
        try:
            from ulfblk_multitenant.context import get_current_tenant

            ctx = get_current_tenant()
            return ctx.tenant_id if ctx else None
        except ImportError:
            return None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
