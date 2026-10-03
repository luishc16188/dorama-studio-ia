"""
Knowledge Ledger - Tracks character knowledge states (knows/believes/can_prove).
Implements the knowledge ledger for tracking what characters know, believe, and can prove.
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

from dorama_studio.core.persistence import PersistenceManager


class KnowledgeState(Enum):
    """Character knowledge states."""
    UNKNOWN = "UNKNOWN"      # No knowledge or awareness
    SUSPICIOUS = "SUSPICIOUS" # Has suspicions but no proof
    AWARE = "AWARE"          # Knows something happened but lacks details
    KNOWS = "KNOWS"          # Has factual knowledge
    BELIEVES = "BELIEVES"    # Has belief based on evidence/reasoning
    CAN_PROVE = "CAN_PROVE"  # Has evidence that would convince others


class KnowledgeSource(Enum):
    """Sources of knowledge acquisition."""
    DIRECT_OBSERVATION = "DIRECT_OBSERVATION"  # Saw it happen
    TESTIMONY = "TESTIMONY"                   # Heard from someone
    DOCUMENTARY = "DOCUMENTARY"               # Found in documents/records
    CIRCUMSTANTIAL = "CIRCUMSTANTIAL"         # Inferred from circumstances
    REASONING = "REASONING"                   # Logical deduction
    INTUITION = "INTUITION"                   # Gut feeling (least reliable)
    AUTHORITY = "AUTHORITY"                   # Trusted source declared it
    REVELATION = "REVELATION"                 # Sudden realization/insight


@dataclass
class KnowledgeEvent:
    """A knowledge acquisition event."""
    event_id: str
    character_id: str
    knowledge_type: str                    # What is known (e.g., "secret_affair", "hidden_money")
    knowledge_state: KnowledgeState       # Current state of knowledge
    source: KnowledgeSource               # How the knowledge was acquired
    source_reference: Optional[str]       # Reference to evidence/source
    timestamp: str                        # ISO timestamp when acquired
    confidence: float                     # 0.0 to 1.0 confidence in knowledge
    context: Dict[str, Any]               # Additional context
    provenance: List[str]                 # Chain of custody for this knowledge


@dataclass
class CharacterKnowledgeState:
    """Complete knowledge state for a character at a point in time."""
    character_id: str
    timestamp: str                        # When this state was recorded
    knowledge: Dict[str, KnowledgeEvent]  # knowledge_type -> KnowledgeEvent
    metadata: Dict[str, Any]              # Additional context


class KnowledgeLedger:
    """
    Tracks what characters know, believe, and can prove over time.
    Prevents characters from using knowledge they haven't acquired.
    """

    def __init__(self, persistence_manager: Optional[PersistenceManager] = None):
        self.persistence_manager = persistence_manager or PersistenceManager()
        # In-memory cache for performance: character_id -> knowledge_state
        self._knowledge_cache: Dict[str, CharacterKnowledgeState] = {}
        self._initialize_cache()

    def _initialize_cache(self) -> None:
        """Initialize knowledge cache from persistence layer."""
        # Load latest knowledge states for all characters
        # For now, we'll start with empty cache and build as we go
        pass

    def acquire_knowledge(
        self,
        character_id: str,
        knowledge_type: str,
        knowledge_state: KnowledgeState,
        source: KnowledgeSource,
        source_reference: Optional[str] = None,
        confidence: float = 1.0,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a character acquiring new knowledge.

        Args:
            character_id: ID of the character acquiring knowledge
            knowledge_type: Type of knowledge being acquired
            knowledge_state: State of knowledge (KNOWS, BELIEVES, etc.)
            source: How the knowledge was acquired
            source_reference: Reference to evidence/source (optional)
            confidence: Confidence level 0.0-1.0
            context: Additional context about the acquisition

        Returns:
            event_id: Unique identifier for this knowledge event
        """
        if context is None:
            context = {}

        # Generate event ID
        import hashlib
        timestamp = datetime.utcnow().isoformat()
        content = f"{character_id}:{knowledge_type}:{timestamp}"
        event_id = hashlib.sha256(content.encode()).hexdigest()[:16]

        # Create knowledge event
        knowledge_event = KnowledgeEvent(
            event_id=event_id,
            character_id=character_id,
            knowledge_type=knowledge_type,
            knowledge_state=knowledge_state,
            source=source,
            source_reference=source_reference,
            timestamp=timestamp,
            confidence=max(0.0, min(1.0, confidence)),
            context=context,
            provenance=[source_reference] if source_reference else []
        )

        # Update cache
        if character_id not in self._knowledge_cache:
            self._knowledge_cache[character_id] = CharacterKnowledgeState(
                character_id=character_id,
                timestamp=timestamp,
                knowledge={},
                metadata={}
            )

        char_state = self._knowledge_cache[character_id]
        char_state.knowledge[knowledge_type] = knowledge_event
        char_state.timestamp = timestamp

        # Persist to database
        self._persist_knowledge_event(knowledge_event)

        return event_id

    def update_knowledge_state(
        self,
        character_id: str,
        knowledge_type: str,
        new_state: KnowledgeState,
        new_source: Optional[KnowledgeSource] = None,
        new_reference: Optional[str] = None,
        new_confidence: Optional[float] = None,
        new_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing knowledge state for a character.

        Args:
            character_id: ID of the character
            knowledge_type: Type of knowledge to update
            new_state: New knowledge state
            new_source: New source of knowledge (optional)
            new_reference: New source reference (optional)
            new_confidence: New confidence level (optional)
            new_context: New context (optional)

        Returns:
            True if updated, False if knowledge_type not found
        """
        if character_id not in self._knowledge_cache:
            return False

        char_state = self._knowledge_cache[character_id]
        if knowledge_type not in char_state.knowledge:
            return False

        # Update the knowledge event
        event = char_state.knowledge[knowledge_type]
        event.knowledge_state = new_state
        if new_source:
            event.source = new_source
        if new_reference:
            event.source_reference = new_reference
            event.provenance.append(new_reference)
        if new_confidence is not None:
            event.confidence = max(0.0, min(1.0, new_confidence))
        if new_context:
            event.context.update(new_context)
        event.timestamp = datetime.utcnow().isoformat()

        # Update cache timestamp
        char_state.timestamp = event.timestamp

        # Persist the update
        self._persist_knowledge_event(event)

        return True

    def get_knowledge_state(
        self,
        character_id: str,
        knowledge_type: str
    ) -> Optional[KnowledgeState]:
        """
        Get the current knowledge state for a character on a specific topic.

        Args:
            character_id: ID of the character
            knowledge_type: Type of knowledge to check

        Returns:
            KnowledgeState or None if character has no knowledge of this type
        """
        if character_id not in self._knowledge_cache:
            return None

        char_state = self._knowledge_cache[character_id]
        if knowledge_type not in char_state.knowledge:
            return None

        return char_state.knowledge[knowledge_type].knowledge_state

    def can_character_know(
        self,
        character_id: str,
        knowledge_type: str
    ) -> bool:
        """
        Check if a character can possibly know something (not completely unknown).

        Args:
            character_id: ID of the character
            knowledge_type: Type of knowledge to check

        Returns:
            True if character has any knowledge beyond UNKNOWN
        """
        state = self.get_knowledge_state(character_id, knowledge_type)
        return state is not None and state != KnowledgeState.UNKNOWN

    def can_character_believe(
        self,
        character_id: str,
        knowledge_type: str
    ) -> bool:
        """
        Check if a character can believe something (has at least BELIEF level).

        Args:
            character_id: ID of the character
            knowledge_type: Type of knowledge to check

        Returns:
            True if character has at least BELIEF state
        """
        state = self.get_knowledge_state(character_id, knowledge_type)
        return state is not None and state in [
            KnowledgeState.BELIEVES,
            KnowledgeState.KNOWS,
            KnowledgeState.CAN_PROVE
        ]

    def can_character_prove(
        self,
        character_id: str,
        knowledge_type: str
    ) -> bool:
        """
        Check if a character can prove something (has evidence).

        Args:
            character_id: ID of the character
            knowledge_type: Type of knowledge to check

        Returns:
            True if character can prove the knowledge
        """
        state = self.get_knowledge_state(character_id, knowledge_type)
        return state == KnowledgeState.CAN_PROVE

    def get_character_knowledge_summary(
        self,
        character_id: str
    ) -> Dict[str, KnowledgeState]:
        """
        Get a summary of all knowledge states for a character.

        Args:
            character_id: ID of the character

        Returns:
            Dictionary mapping knowledge_type -> KnowledgeState
        """
        if character_id not in self._knowledge_cache:
            return {}

        char_state = self._knowledge_cache[character_id]
        return {
            knowledge_type: event.knowledge_state
            for knowledge_type, event in char_state.knowledge.items()
        }

    def get_knowledge_events(
        self,
        character_id: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[KnowledgeEvent]:
        """
        Retrieve knowledge events with optional filtering.

        Args:
            character_id: Filter by character ID (optional)
            knowledge_type: Filter by knowledge type (optional)
            start_time: Filter by start time (ISO format, optional)
            end_time: Filter by end time (ISO format, optional)
            limit: Maximum number of events to return

        Returns:
            List of KnowledgeEvent objects
        """
        # For now, return from cache - in full implementation would query database
        events = []

        if character_id:
            # Filter by specific character
            if character_id in self._knowledge_cache:
                char_state = self._knowledge_cache[character_id]
                events.extend(char_state.knowledge.values())
        else:
            # All characters
            for char_state in self._knowledge_cache.values():
                events.extend(char_state.knowledge.values())

        # Apply filters
        if knowledge_type:
            events = [e for e in events if e.knowledge_type == knowledge_type]
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]

        # Sort by timestamp (newest first) and limit
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]

    def _persist_knowledge_event(self, event: KnowledgeEvent) -> None:
        """Persist a knowledge event to the database."""
        # This would store in a knowledge_events table
        # For now, we'll rely on the persistence manager's generation logs
        # In a full implementation, this would have its own table
        pass

    def get_knowledge_for_beat(
        self,
        character_ids: List[str],
        beat_timestamp: str
    ) -> Dict[str, Dict[str, KnowledgeState]]:
        """
        Get knowledge states for multiple characters at a specific beat timestamp.

        Args:
            character_ids: List of character IDs to check
            beat_timestamp: Timestamp of the beat (ISO format)

        Returns:
            Dictionary mapping character_id -> {knowledge_type -> KnowledgeState}
        """
        result = {}
        for char_id in character_ids:
            result[char_id] = self.get_character_knowledge_summary(char_id)
        return result

    def validate_knowledge_usage(
        self,
        character_id: str,
        knowledge_type: str,
        required_state: KnowledgeState
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a character has sufficient knowledge state for a given usage.

        Args:
            character_id: ID of the character
            knowledge_type: Type of knowledge being used
            required_state: Minimum knowledge state required

        Returns:
            Tuple of (is_valid, error_message)
        """
        current_state = self.get_knowledge_state(character_id, knowledge_type)

        if current_state is None:
            return False, f"Character {character_id} has no knowledge of {knowledge_type}"

        # Define knowledge state hierarchy (higher index = more knowledge)
        knowledge_hierarchy = [
            KnowledgeState.UNKNOWN,
            KnowledgeState.SUSPICIOUS,
            KnowledgeState.AWARE,
            KnowledgeState.KNOWS,
            KnowledgeState.BELIEVES,
            KnowledgeState.CAN_PROVE
        ]

        try:
            current_level = knowledge_hierarchy.index(current_state)
            required_level = knowledge_hierarchy.index(required_state)

            if current_level >= required_level:
                return True, None
            else:
                return False, f"Character {character_id} has {current_state.value} knowledge of {knowledge_type}, but {required_state.value} is required"
        except ValueError:
            return False, f"Invalid knowledge state: {current_state} or {required_state}"


# Global knowledge ledger instance
knowledge_ledger = KnowledgeLedger()