"""
Error Memory Bank - operationalizes MEMORIA_DE_ERRORES.md (GAP 4 fix)
Automatic consultation and registration of errors
"""

import json
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class ErrorCategory(str, Enum):
    CONS = "CONS"  # Consistency visual
    PROMPT = "PROMPT"  # Prompt engineering
    VFX = "VFX"  # Visual effects
    AUDIO = "AUDIO"  # Audio/voice
    RET = "RET"  # Retention
    SYNC = "SYNC"  # Pipeline sync
    LLM = "LLM"  # LLM output quality


class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    BLOCKED = "blocked"


@dataclass
class ErrorRecord:
    """Single error record matching MEMORIA_DE_ERRORES.md schema"""

    id: str  # ERR-YYYYMMDD-NNN
    timestamp: str
    agent_origin: str
    category: ErrorCategory
    severity: ErrorSeverity
    description: str
    context: dict[str, Any]
    root_cause: str
    fix_applied: str
    preventive_rule: str
    status: ErrorStatus = ErrorStatus.OPEN
    recurrence_count: int = 0
    related_errors: list[str] = field(default_factory=list)
    resolved_at: str | None = None
    resolved_by: str | None = None


class ErrorMemoryBank:
    """
    Runtime error memory - consults MEMORIA_DE_ERRORES.md before execution
    and auto-registers new errors with escalation.
    """

    def __init__(self, memory_path: Path):
        self.memory_path = memory_path
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._errors: dict[str, ErrorRecord] = {}
        self._load()

    def _load(self):
        """Load from JSONL or JSON file"""
        with self._lock:
            self._errors.clear()

            # Try JSON first
            if self.memory_path.suffix == ".json":
                try:
                    with open(self.memory_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for item in data:
                            self._errors[item["id"]] = ErrorRecord(**item)
                    return
                except:
                    pass

            # Try JSONL
            jsonl_path = self.memory_path.with_suffix(".jsonl")
            if jsonl_path.exists():
                with open(jsonl_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            item = json.loads(line.strip())
                            self._errors[item["id"]] = ErrorRecord(**item)
                        except:
                            continue

    def _save(self):
        """Save to JSON"""
        with self._lock:
            data = [asdict(e) for e in self._errors.values()]
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def _next_id(self) -> str:
        """Generate next error ID"""
        date_str = datetime.now().strftime("%Y%m%d")
        existing = [e for e in self._errors.keys() if e.startswith(f"ERR-{date_str}-")]
        next_num = len(existing) + 1
        return f"ERR-{date_str}-{next_num:03d}"

    def register_error(
        self,
        agent: str,
        category: ErrorCategory,
        description: str,
        fix: str,
        context: dict[str, Any] | None = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        root_cause: str = "Pending analysis",
    ) -> ErrorRecord:
        """Register new error with auto-escalation on recurrence"""
        with self._lock:
            # Check for duplicates
            for existing in self._errors.values():
                if (
                    existing.agent_origin == agent
                    and existing.category == category
                    and existing.description == description
                    and existing.status in (ErrorStatus.OPEN, ErrorStatus.IN_PROGRESS)
                ):

                    # Increment recurrence
                    existing.recurrence_count += 1
                    existing.severity = self._escalate_severity(
                        existing.severity, existing.recurrence_count
                    )
                    self._save()
                    return existing

            # Create new record
            record = ErrorRecord(
                id=self._next_id(),
                timestamp=datetime.now().isoformat(),
                agent_origin=agent,
                category=category,
                severity=severity,
                description=description,
                context=context or {},
                root_cause=root_cause,
                fix_applied=fix,
                preventive_rule=self._generate_preventive_rule(
                    category, description, fix
                ),
                status=ErrorStatus.OPEN,
            )

            self._errors[record.id] = record
            self._save()

            return record

    def _escalate_severity(self, current: ErrorSeverity, count: int) -> ErrorSeverity:
        """Auto-escalate severity based on recurrence"""
        if count >= 3:
            return ErrorSeverity.CRITICAL
        elif count >= 2:
            return ErrorSeverity.HIGH
        elif count >= 1:
            return ErrorSeverity.MEDIUM
        return current

    def _generate_preventive_rule(
        self, category: ErrorCategory, description: str, fix: str
    ) -> str:
        """Generate actionable preventive rule from error"""
        templates = {
            ErrorCategory.CONS: "Before rendering: validate CLIP similarity >= 0.88 using locked seed. "
            "Run CharacterConsistencyValidator on reference sheet.",
            ErrorCategory.PROMPT: "Review prompt structure: use explicit constraints, examples, and negative prompts. "
            "Test with 3 variations before pipeline.",
            ErrorCategory.VFX: "Pre-validate keyframes at 50% resolution. Check hand/face consistency before full render.",
            ErrorCategory.AUDIO: "Verify TTS timing matches lip-sync requirements. Use ElevenLabs v3 with stability > 0.7.",
            ErrorCategory.RET: "Insert visual/emotional hook every 8-10s. Avoid >2.5s static exposition.",
            ErrorCategory.SYNC: "Verify all agent inputs/outputs match Pydantic contracts. Add schema validation.",
            ErrorCategory.LLM: "Lower temperature for structured output. Use JSON mode with Pydantic schema.",
        }
        return templates.get(category, f"Apply fix: {fix}. Context: {description}")

    def get_preventive_rules(
        self,
        agent: str,
        category: ErrorCategory | None = None,
        min_severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    ) -> list[str]:
        """Get preventive rules for agent (called in BaseAgent.__init__)"""
        with self._lock:
            severity_order = {
                ErrorSeverity.LOW: 0,
                ErrorSeverity.MEDIUM: 1,
                ErrorSeverity.HIGH: 2,
                ErrorSeverity.CRITICAL: 3,
            }
            min_level = severity_order[min_severity]

            rules = []
            for err in self._errors.values():
                if err.agent_origin != agent:
                    continue
                if category and err.category != category:
                    continue
                if severity_order.get(err.severity, 0) < min_level:
                    continue
                if err.status != ErrorStatus.RESOLVED:
                    continue
                if err.preventive_rule:
                    rules.append(err.preventive_rule)

            return list(dict.fromkeys(rules))  # Deduplicate preserving order

    def resolve_error(self, error_id: str, resolved_by: str) -> bool:
        """Mark error as resolved"""
        with self._lock:
            if error_id in self._errors:
                err = self._errors[error_id]
                err.status = ErrorStatus.RESOLVED
                err.resolved_at = datetime.now().isoformat()
                err.resolved_by = resolved_by
                self._save()
                return True
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics"""
        with self._lock:
            total = len(self._errors)
            by_agent = {}
            by_category = {}
            by_status = {}

            for err in self._errors.values():
                by_agent[err.agent_origin] = by_agent.get(err.agent_origin, 0) + 1
                by_category[err.category.value] = (
                    by_category.get(err.category.value, 0) + 1
                )
                by_status[err.status.value] = by_status.get(err.status.value, 0) + 1

            return {
                "total_errors": total,
                "by_agent": by_agent,
                "by_category": by_category,
                "by_status": by_status,
                "critical_unresolved": sum(
                    1
                    for e in self._errors.values()
                    if e.severity == ErrorSeverity.CRITICAL
                    and e.status != ErrorStatus.RESOLVED
                ),
            }
