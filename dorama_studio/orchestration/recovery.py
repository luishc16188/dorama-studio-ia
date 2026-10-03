"""
Failure recovery and replanning for DORAMA STUDIO orchestration.
Handles failure analysis, recovery strategies, and automatic replanning.
"""

import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of failures that can occur."""
    AGENT_ERROR = "agent_error"           # Agent threw exception
    QUALITY_FAILURE = "quality_failure"   # QC detected issues
    TIMEOUT = "timeout"                    # Operation timed out
    RESOURCE_EXHAUSTED = "resource_exhausted"  # Memory, disk, API limits
    VALIDATION_ERROR = "validation_error"  # Input/output validation failed
    CHECKPOINT_ERROR = "checkpoint_error"  # Failed to save/load checkpoint
    HUMAN_REJECTION = "human_rejection"    # Human rejected at HITL
    UNKNOWN = "unknown"


class RecoveryAction(Enum):
    """Possible recovery actions."""
    RETRY_SAME = "retry_same"                 # Retry the same node
    RETRY_WITH_FALLBACK = "retry_fallback"    # Retry with fallback config
    SKIP_NODE = "skip_node"                   # Skip node, use default/empty
    REGENERATE_PARTIAL = "regenerate_partial"  # Regenerate specific artifacts
    REGENERATE_FULL = "regenerate_full"       # Full episode regeneration
    REPLAN = "replan"                         # Replan from earlier node
    ESCALATE = "escalate"                     # Escalate to human
    FAIL = "fail"                             # Mark as failed


@dataclass
class FailureContext:
    """Context information about a failure."""
    node_name: str
    failure_type: FailureType
    error: Exception
    attempt: int
    state_snapshot: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryPlan:
    """Plan for recovering from a failure."""
    action: RecoveryAction
    target_node: str | None = None
    fallback_config: dict[str, Any] | None = None
    regenerate_artifacts: list[str] = field(default_factory=list)
    skip_nodes: list[str] = field(default_factory=list)
    replan_from: str | None = None
    reason: str = ""
    estimated_retries: int = 1


class FailureAnalyzer:
    """Analyzes failures and recommends recovery actions."""

    def __init__(self):
        # Failure type -> default recovery action mapping
        self.default_recovery = {
            FailureType.AGENT_ERROR: RecoveryAction.RETRY_WITH_FALLBACK,
            FailureType.QUALITY_FAILURE: RecoveryAction.REGENERATE_PARTIAL,
            FailureType.TIMEOUT: RecoveryAction.RETRY_WITH_FALLBACK,
            FailureType.RESOURCE_EXHAUSTED: RecoveryAction.RETRY_WITH_FALLBACK,
            FailureType.VALIDATION_ERROR: RecoveryAction.RETRY_SAME,
            FailureType.CHECKPOINT_ERROR: RecoveryAction.RETRY_SAME,
            FailureType.HUMAN_REJECTION: RecoveryAction.ESCALATE,
            FailureType.UNKNOWN: RecoveryAction.RETRY_SAME,
        }

        # Node-specific recovery overrides
        self.node_recovery_overrides = {
            "quality_check": {
                FailureType.QUALITY_FAILURE: RecoveryAction.REGENERATE_PARTIAL,
            },
            "visual_render": {
                FailureType.RESOURCE_EXHAUSTED: RecoveryAction.RETRY_WITH_FALLBACK,
                FailureType.TIMEOUT: RecoveryAction.RETRY_WITH_FALLBACK,
            },
            "hitl_episode_qc": {
                FailureType.HUMAN_REJECTION: RecoveryAction.REPLAN,
            },
        }

    def analyze(self, context: FailureContext) -> RecoveryPlan:
        """
        Analyze failure and create recovery plan.

        Args:
            context: Failure context

        Returns:
            RecoveryPlan with recommended action
        """
        # Determine failure type if not set
        if context.failure_type == FailureType.UNKNOWN:
            context.failure_type = self._classify_failure(context.error)

        # Get default action for failure type
        default_action = self.default_recovery.get(
            context.failure_type,
            RecoveryAction.RETRY_SAME
        )

        # Check node-specific overrides
        node_overrides = self.node_recovery_overrides.get(context.node_name, {})
        action = node_overrides.get(context.failure_type, default_action)

        # Adjust based on attempt count
        if context.attempt >= 3 and action == RecoveryAction.RETRY_SAME:
            action = RecoveryAction.RETRY_WITH_FALLBACK
        if context.attempt >= 5:
            action = RecoveryAction.REGENERATE_FULL

        # Build recovery plan
        plan = self._build_plan(context, action)
        return plan

    def _classify_failure(self, error: Exception) -> FailureType:
        """Classify exception into failure type."""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()

        if any(kw in error_str for kw in ["timeout", "timed out"]):
            return FailureType.TIMEOUT
        if any(kw in error_str for kw in ["memory", "disk", "quota", "rate limit", "resource"]):
            return FailureType.RESOURCE_EXHAUSTED
        if any(kw in error_str for kw in ["validation", "invalid", "schema", "pydantic"]):
            return FailureType.VALIDATION_ERROR
        if any(kw in error_str for kw in ["checkpoint", "persist", "save", "load"]):
            return FailureType.CHECKPOINT_ERROR
        if any(kw in error_str for kw in ["rejected", "denied", "not approved", "human"]):
            return FailureType.HUMAN_REJECTION
        if any(kw in error_str for kw in ["quality", "fail", "critical"]):
            return FailureType.QUALITY_FAILURE

        return FailureType.AGENT_ERROR

    def _build_plan(self, context: FailureContext, action: RecoveryAction) -> RecoveryPlan:
        """Build detailed recovery plan based on action."""
        plan = RecoveryPlan(action=action, reason=f"Recovering from {context.failure_type.value}")

        if action == RecoveryAction.RETRY_SAME:
            plan.target_node = context.node_name
            plan.reason += " - Retrying same node"

        elif action == RecoveryAction.RETRY_WITH_FALLBACK:
            plan.target_node = context.node_name
            plan.fallback_config = self._get_fallback_config(context.node_name)
            plan.reason += " - Retrying with fallback configuration"

        elif action == RecoveryAction.SKIP_NODE:
            plan.skip_nodes = [context.node_name]
            plan.reason += " - Skipping node, using defaults"

        elif action == RecoveryAction.REGENERATE_PARTIAL:
            plan.target_node = context.node_name
            plan.regenerate_artifacts = self._get_regeneratable_artifacts(context.node_name)
            plan.reason += " - Regenerating affected artifacts"

        elif action == RecoveryAction.REGENERATE_FULL:
            plan.action = RecoveryAction.REPLAN
            plan.replan_from = "episode_architect"
            plan.reason += " - Full regeneration via replan"

        elif action == RecoveryAction.REPLAN:
            plan.replan_from = self._get_replan_point(context.node_name)
            plan.reason += f" - Replanning from {plan.replan_from}"

        elif action == RecoveryAction.ESCALATE:
            plan.reason += " - Escalating to human operator"

        elif action == RecoveryAction.FAIL:
            plan.reason += " - Marking as failed"

        return plan

    def _get_fallback_config(self, node_name: str) -> dict[str, Any]:
        """Get fallback configuration for a node."""
        fallbacks = {
            "visual_render": {"quality": "low", "timeout": 300},
            "voice_render": {"model": "fast", "quality": "standard"},
            "music_render": {"duration": 30, "complexity": "simple"},
            "quality_check": {"strict_mode": False},
        }
        return fallbacks.get(node_name, {})

    def _get_regeneratable_artifacts(self, node_name: str) -> list[str]:
        """Get list of artifacts that can be regenerated for a node."""
        artifact_map = {
            "visual_render": ["visual_artifacts"],
            "voice_render": ["voice_artifacts"],
            "sfx_render": ["sfx_artifacts"],
            "music_render": ["music_artifacts"],
            "audio_mix": ["master_audio"],
            "edit": ["edit_timeline"],
            "subtitles": ["subtitles"],
            "quality_check": ["quality_report"],
            "cliffhanger_engine": ["cliffhanger"],
            "retention_review": ["retention_actions"],
        }
        return artifact_map.get(node_name, [])

    def _get_replan_point(self, failed_node: str) -> str:
        """Determine where to replan from based on failed node."""
        # Map of node -> earliest safe replan point
        replan_map = {
            "visual_render": "prompt_compile",
            "voice_render": "prompt_compile",
            "sfx_render": "prompt_compile",
            "music_render": "prompt_compile",
            "audio_mix": "visual_render",
            "edit": "audio_mix",
            "subtitles": "edit",
            "quality_check": "subtitles",
            "cliffhanger_engine": "master_writer",
            "retention_review": "master_writer",
            "dialogue_polish": "master_writer",
            "hook_engine": "episode_architect",
        }
        return replan_map.get(failed_node, "episode_architect")


class Replanner:
    """Handles replanning of episode production after failures."""

    def __init__(self, analyzer: FailureAnalyzer | None = None):
        self.analyzer = analyzer or FailureAnalyzer()

    def create_replan(
        self,
        failed_node: str,
        error: Exception,
        current_state: dict[str, Any],
        attempt: int = 1
    ) -> dict[str, Any]:
        """
        Create a replan for the failed production.

        Args:
            failed_node: Name of node that failed
            error: Exception that occurred
            current_state: Current pipeline state
            attempt: Current attempt number

        Returns:
            Replan specification
        """
        context = FailureContext(
            node_name=failed_node,
            failure_type=FailureType.UNKNOWN,
            error=error,
            attempt=attempt,
            state_snapshot=copy.deepcopy(current_state),
        )

        plan = self.analyzer.analyze(context)

        replan = {
            "action": plan.action.value,
            "reason": plan.reason,
            "target_node": plan.target_node,
            "replan_from": plan.replan_from,
            "fallback_config": plan.fallback_config,
            "regenerate_artifacts": plan.regenerate_artifacts,
            "skip_nodes": plan.skip_nodes,
            "original_failed_node": failed_node,
            "error": str(error),
            "attempt": attempt,
        }

        logger.info(f"Created replan: {plan.action.value} - {plan.reason}")
        return replan

    def apply_replan(
        self,
        state: dict[str, Any],
        replan: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Apply replan to state.

        Args:
            state: Current state
            replan: Replan specification

        Returns:
            Modified state
        """
        new_state = copy.deepcopy(state)

        # Remove regenerated artifacts from refs
        for artifact_type in replan.get("regenerate_artifacts", []):
            if artifact_type in new_state.get("artifact_refs", {}):
                del new_state["artifact_refs"][artifact_type]

        # Update stage to replan point
        if replan.get("replan_from"):
            new_state["stage"] = f"replan_from_{replan['replan_from']}"

        # Store replan info
        new_state["regeneration_plan"] = replan
        new_state["retry_budget"] = max(0, new_state.get("retry_budget", 3) - 1)

        return new_state


class RecoveryManager:
    """High-level recovery management for the pipeline."""

    def __init__(self):
        self.analyzer = FailureAnalyzer()
        self.replanner = Replanner(self.analyzer)
        self.failure_history: list[FailureContext] = []

    def handle_failure(
        self,
        node_name: str,
        error: Exception,
        state: dict[str, Any],
        attempt: int = 1
    ) -> RecoveryPlan:
        """
        Handle a failure and return recovery plan.

        Args:
            node_name: Name of failed node
            error: Exception that occurred
            state: Current pipeline state
            attempt: Current attempt number

        Returns:
            RecoveryPlan with recommended action
        """
        context = FailureContext(
            node_name=node_name,
            failure_type=FailureType.UNKNOWN,
            error=error,
            attempt=attempt,
            state_snapshot=copy.deepcopy(state),
        )

        # Record failure
        self.failure_history.append(context)

        # Analyze and plan recovery
        plan = self.analyzer.analyze(context)

        logger.info(
            f"Failure handled: {node_name} - {plan.action.value} - {plan.reason}"
        )

        return plan

    def apply_recovery(
        self,
        state: dict[str, Any],
        plan: RecoveryPlan
    ) -> dict[str, Any]:
        """Apply recovery plan to state."""
        replan_spec = {
            "action": plan.action.value,
            "reason": plan.reason,
            "target_node": plan.target_node,
            "replan_from": plan.replan_from,
            "fallback_config": plan.fallback_config,
            "regenerate_artifacts": plan.regenerate_artifacts,
            "skip_nodes": plan.skip_nodes,
        }
        return self.replanner.apply_replan(state, replan_spec)

    def get_failure_stats(self) -> dict[str, Any]:
        """Get statistics about failures."""
        if not self.failure_history:
            return {"total": 0}

        by_type = {}
        by_node = {}

        for f in self.failure_history:
            by_type[f.failure_type.value] = by_type.get(f.failure_type.value, 0) + 1
            by_node[f.node_name] = by_node.get(f.node_name, 0) + 1

        return {
            "total": len(self.failure_history),
            "by_type": by_type,
            "by_node": by_node,
            "latest": {
                "node": self.failure_history[-1].node_name,
                "type": self.failure_history[-1].failure_type.value,
                "time": self.failure_history[-1].timestamp.isoformat(),
            }
        }

    def should_escalate(self, node_name: str, attempt: int) -> bool:
        """Check if failure should be escalated."""
        # Count failures for this node
        node_failures = sum(1 for f in self.failure_history if f.node_name == node_name)

        # Escalate after 3 attempts on same node
        if attempt >= 3 and node_failures >= 3:
            return True

        # Escalate if total failures > 10
        if len(self.failure_history) > 10:
            return True

        return False


# Default recovery manager instance
default_recovery_manager = RecoveryManager()
