"""
Core agent infrastructure - base classes and feedback loop (GAP 2 fix)
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class AnalyticsOutput:
    """Output from Analytics Engine (Agent 20)"""

    episode_id: str
    retention_curve: list[float]  # Retention at each second
    drop_off_points: list[int]  # Seconds where viewers drop
    winning_hook_category: str
    losing_hook_category: str
    avg_watch_time: float
    completion_rate: float
    emotional_peaks: list[tuple[int, str]]  # (second, emotion)
    timestamp: datetime = field(default_factory=datetime.now)


class FeedbackLoop:
    """
    Automated feedback injection - closes the loop between Analytics
    and Writer/Hook agents (GAP 2 from autodiagnostico)
    """

    def __init__(self, memory_path: Path | None = None):
        self.memory_path = memory_path or Path("memory/feedback_history.json")
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._history: list[dict] = []
        self._load_history()

    def _load_history(self):
        if self.memory_path.exists():
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
            except:
                self._history = []

    def _save_history(self):
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self._history[-1000:], f, ensure_ascii=False, indent=2)
        except:
            pass

    def inject_rules(self, agent_name: str, analytics: AnalyticsOutput) -> str:
        """
        Generate override prompt for target agent based on analytics.
        Returns the override_prompt to prepend to agent's system prompt.
        """
        overrides = {
            "MasterWriter": self._generate_writer_override(analytics),
            "HookEngine": self._generate_hook_override(analytics),
            "CharacterDirector": self._generate_character_override(analytics),
            "VisualDirector": self._generate_visual_override(analytics),
        }

        override = overrides.get(agent_name, "")

        # Record injection
        self._history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "agent": agent_name,
                "episode": analytics.episode_id,
                "override_length": len(override),
                "drop_offs": analytics.drop_off_points,
            }
        )
        self._save_history()

        return override

    def _generate_writer_override(self, analytics: AnalyticsOutput) -> str:
        """Generate override for Master Writer"""
        drop_off_str = ", ".join(f"{s}s" for s in analytics.drop_off_points[:3])
        peak_str = ", ".join(f"{s}s:{e}" for s, e in analytics.emotional_peaks[:3])

        return (
            f"\n\n=== ANALYTICS FEEDBACK (Episode {analytics.episode_id}) ===\n"
            f"CRITICAL: Drop-offs detected at seconds: {drop_off_str}.\n"
            f"MAX 2.5s of exposition without visual change after these points.\n"
            f"Emotional peaks at: {peak_str}. REINFORCE these moments.\n"
            f"Completion rate: {analytics.completion_rate:.1%}. "
            f"{'INCREASE pacing if < 40%.' if analytics.completion_rate < 0.4 else 'MAINTAIN pacing.'}\n"
            f"=== END FEEDBACK ===\n"
        )

    def _generate_hook_override(self, analytics: AnalyticsOutput) -> str:
        """Generate override for Hook Engine"""
        return (
            f"\n\n=== HOOK OPTIMIZATION (Episode {analytics.episode_id}) ===\n"
            f"WINNING CATEGORY: '{analytics.winning_hook_category}' - DOUBLE DOWN.\n"
            f"LOSING CATEGORY: '{analytics.losing_hook_category}' - AVOID completely.\n"
            f"Retention at 3s: {analytics.retention_curve[2]*100:.0f}% "
            f"{'BOOST intrigue if < 70%' if analytics.retention_curve[2] < 0.7 else 'MAINTAIN'}\n"
            f"=== END HOOK FEEDBACK ===\n"
        )

    def _generate_character_override(self, analytics: AnalyticsOutput) -> str:
        return (
            f"\n\n=== CHARACTER FEEDBACK (Episode {analytics.episode_id}) ===\n"
            f"Emotional authenticity needs work. Peak emotions: "
            f"{', '.join(e for _, e in analytics.emotional_peaks[:3])}.\n"
            f"Ensure character reactions match these peaks.\n"
            f"=== END CHARACTER FEEDBACK ===\n"
        )

    def _generate_visual_override(self, analytics: AnalyticsOutput) -> str:
        return (
            f"\n\n=== VISUAL FEEDBACK (Episode {analytics.episode_id}) ===\n"
            f"Drop-off at {analytics.drop_off_points[0] if analytics.drop_off_points else 'N/A'}s "
            f"suggests visual fatigue. INCREASE shot variety after this point.\n"
            f"=== END VISUAL FEEDBACK ===\n"
        )


class BaseAgent(ABC):
    """
    Base class for all 21 agents - integrates ErrorMemory and FeedbackLoop
    """

    def __init__(
        self,
        name: str,
        error_memory: Optional["ErrorMemoryBank"] = None,
        feedback_loop: FeedbackLoop | None = None,
    ):
        self.name = name
        self.error_memory = error_memory
        self.feedback_loop = feedback_loop
        self.preventive_rules: list[str] = []

        # Load preventive rules from error memory
        if self.error_memory:
            self.preventive_rules = self.error_memory.get_preventive_rules(self.name)

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Execute agent logic"""

    def build_prompt(
        self, base_prompt: str, analytics: AnalyticsOutput | None = None
    ) -> str:
        """Build final prompt with preventive rules and feedback injection"""
        parts = [base_prompt]

        # Add preventive rules from error memory
        if self.preventive_rules:
            parts.append("\n=== PREVENTIVE RULES (from Error Memory) ===")
            parts.extend(f"- {rule}" for rule in self.preventive_rules)
            parts.append("=== END PREVENTIVE RULES ===\n")

        # Add feedback loop injection if analytics provided
        if analytics and self.feedback_loop:
            override = self.feedback_loop.inject_rules(self.name, analytics)
            if override:
                parts.append(override)

        return "\n".join(parts)

    def register_error(self, category: str, description: str, fix: str):
        """Register an error for future prevention"""
        if self.error_memory:
            self.error_memory.register_error(
                agent=self.name, category=category, description=description, fix=fix
            )
            # Refresh preventive rules
            self.preventive_rules = self.error_memory.get_preventive_rules(self.name)

    def quality_gate(self, episode_id: str | None, episode_data: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Quality Gate - 100 point validation across 15 dimensions.
        Returns (approved, deficiencies).
        """
        checks = [
            ("hook_0_3s", 20),
            ("conflict_concrete", 15),
            ("protagonist_desire_clarified", 15),
            ("unresolved_question", 15),
            ("situation_worsens", 15),
            ("partial_answer", 10),
            ("surprise_element", 10),
            ("strong_cliffhanger", 10),
            ("emotional_impact", 5),
            ("show_dont_tell", 5),
            ("dialogue_advances_story", 5),
            ("dialogue_delivery_present", 5),
            ("micro_expressions_present", 5),
            ("silence_drop_before_revelation", 5),
            ("fractal_formula_applied", 5),
        ]

        score = sum(pts for field, pts in checks if episode_data.get(field))
        approved = score >= 70  # 70% threshold for approval
        deficiencies = [field for field, pts in checks if not episode_data.get(field)]

        return approved, deficiencies
