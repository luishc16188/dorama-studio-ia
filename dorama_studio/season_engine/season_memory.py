"""
Season Memory - Phase 6
Long-term memory system for tracking facts, events, and context across a 40-episode season.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class FactType(str, Enum):
    """Types of facts stored in season memory."""
    CHARACTER_FACT = "character_fact"
    PLOT_FACT = "plot_fact"
    WORLD_FACT = "world_fact"
    RELATIONSHIP_FACT = "relationship_fact"
    OBJECT_FACT = "object_fact"
    LOCATION_FACT = "location_fact"
    REVEAL_FACT = "reveal_fact"
    THEME_FACT = "theme_fact"


class FactStatus(str, Enum):
    """Status of a fact in the narrative."""
    ESTABLISHED = "established"      # Confirmed true in narrative
    REVEALED = "revealed"            # Was hidden, now known to audience
    CONTRADICTED = "contradicted"    # Proven false
    RETCONNED = "retconned"          # Changed by later revelation
    SPECULATED = "speculated"        # Hinted but not confirmed
    FORGOTTEN = "forgotten"          # No longer relevant/referenced


class Fact(BaseModel):
    """A single fact stored in season memory."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    fact_id: str
    fact_type: FactType
    content: str  # The fact itself
    status: FactStatus = FactStatus.ESTABLISHED

    # Source tracking
    source_episode: int = Field(ge=1, le=40)
    source_scene: str | None = None
    source_character: str | None = None

    # Dependencies
    depends_on: list[str] = Field(default_factory=list)  # Other fact_ids this depends on
    contradicts: list[str] = Field(default_factory=list)  # Fact_ids this contradicts
    supports: list[str] = Field(default_factory=list)    # Fact_ids this supports

    # Audience knowledge
    audience_knows_since: int | None = None  # Episode when audience learned
    characters_know: list[str] = Field(default_factory=list)  # Who knows this

    # Relevance
    importance: Literal["critical", "major", "minor", "flavor"] = "minor"
    tags: list[str] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContextQuery(BaseModel):
    """Query for retrieving relevant context from season memory."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    query_text: str
    current_episode: int
    character_focus: str | None = None
    location_focus: str | None = None
    fact_types: list[FactType] | None = None
    max_results: int = 10
    include_speculated: bool = False
    include_forgotten: bool = False
    min_importance: Literal["critical", "major", "minor", "flavor"] = "flavor"


class ContextResult(BaseModel):
    """Result of a context query."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    query: ContextQuery
    facts: list[Fact] = Field(default_factory=list)
    summary: str = ""
    relevant_episodes: list[int] = Field(default_factory=list)
    open_loops: list[str] = Field(default_factory=list)
    pending_reveals: list[str] = Field(default_factory=list)


class SeasonMemory(BaseModel):
    """
    Long-term memory for a season.
    Stores facts, tracks audience knowledge, manages open questions.
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid", arbitrary_types_allowed=True)

    season_id: str
    total_episodes: int = 40

    # Fact storage
    facts: dict[str, Fact] = Field(default_factory=dict)
    facts_by_episode: dict[int, list[str]] = Field(default_factory=lambda: defaultdict(list))
    facts_by_type: dict[FactType, list[str]] = Field(default_factory=lambda: defaultdict(list))
    facts_by_character: dict[str, list[str]] = Field(default_factory=lambda: defaultdict(list))

    # Audience knowledge tracking
    audience_knowledge: dict[int, list[str]] = Field(default_factory=lambda: defaultdict(list))  # ep -> fact_ids

    # Character knowledge
    character_knowledge: dict[str, dict[int, list[str]]] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(list)))

    # Open questions/mysteries
    open_questions: dict[str, dict[str, Any]] = Field(default_factory=dict)

    # Theme tracking
    theme_development: dict[str, list[dict[str, Any]]] = Field(default_factory=lambda: defaultdict(list))

    def add_fact(self, fact: Fact) -> None:
        """Add a fact to memory."""
        self.facts[fact.fact_id] = fact
        self.facts_by_episode[fact.source_episode].append(fact.fact_id)
        self.facts_by_type[fact.fact_type].append(fact.fact_id)

        if fact.source_character:
            self.facts_by_character[fact.source_character].append(fact.fact_id)

        # Track audience knowledge
        if fact.audience_knows_since:
            self.audience_knowledge[fact.audience_knows_since].append(fact.fact_id)

        # Track character knowledge
        for char in fact.characters_know:
            self.character_knowledge[char][fact.source_episode].append(fact.fact_id)

    def get_fact(self, fact_id: str) -> Fact | None:
        """Get a fact by ID."""
        return self.facts.get(fact_id)

    def get_facts_for_episode(self, episode: int, fact_type: FactType | None = None) -> list[Fact]:
        """Get all facts established in an episode."""
        fact_ids = self.facts_by_episode.get(episode, [])
        facts = [self.facts[fid] for fid in fact_ids if fid in self.facts]
        if fact_type:
            facts = [f for f in facts if f.fact_type == fact_type]
        return facts

    def get_facts_by_type(self, fact_type: FactType) -> list[Fact]:
        """Get all facts of a specific type."""
        fact_ids = self.facts_by_type.get(fact_type, [])
        return [self.facts[fid] for fid in fact_ids if fid in self.facts]

    def get_facts_for_character(self, character_id: str) -> list[Fact]:
        """Get all facts associated with a character."""
        fact_ids = self.facts_by_character.get(character_id, [])
        return [self.facts[fid] for fid in fact_ids if fid in self.facts]

    def query(self, query: ContextQuery) -> ContextResult:
        """
        Query memory for relevant context.
        Returns filtered facts and summary.
        """
        results = []

        # Filter by episode (only facts established up to current episode)
        candidate_facts = [
            f for f in self.facts.values()
            if f.source_episode <= query.current_episode
        ]

        # Filter by fact type
        if query.fact_types:
            candidate_facts = [f for f in candidate_facts if f.fact_type in query.fact_types]

        # Filter by importance
        importance_order = {"critical": 4, "major": 3, "minor": 2, "flavor": 1}
        min_imp = importance_order[query.min_importance]
        candidate_facts = [f for f in candidate_facts if importance_order[f.importance] >= min_imp]

        # Filter by status
        if not query.include_speculated:
            candidate_facts = [f for f in candidate_facts if f.status != FactStatus.SPECULATED]
        if not query.include_forgotten:
            candidate_facts = [f for f in candidate_facts if f.status != FactStatus.FORGOTTEN]

        # Filter by character focus
        if query.character_focus:
            candidate_facts = [
                f for f in candidate_facts
                if query.character_focus in f.characters_know or f.source_character == query.character_focus
            ]

        # Filter by location (would need location tagging on facts)
        # Simplified for now

        # Sort by relevance (importance + recency)
        importance_order = {"critical": 4, "major": 3, "minor": 2, "flavor": 1}
        candidate_facts.sort(
            key=lambda f: (importance_order[f.importance], f.source_episode),
            reverse=True
        )

        # Take top results
        results = candidate_facts[:query.max_results]

        # Build summary
        fact_summaries = [f"{f.fact_type.value}: {f.content[:80]}..." for f in results]
        summary = f"Found {len(results)} relevant facts for episode {query.current_episode}. " + "; ".join(fact_summaries[:5])

        # Find relevant episodes
        relevant_eps = sorted(set(f.source_episode for f in results))

        # Find open loops (facts with SPECULATED status or unresolved reveals)
        open_loops = [
            f.fact_id for f in self.facts.values()
            if f.status in [FactStatus.SPECULATED, FactStatus.ESTABLISHED]
            and f.fact_type in [FactType.REVEAL_FACT, FactType.PLOT_FACT]
            and f.source_episode <= query.current_episode
        ][:10]

        # Find pending reveals (facts audience doesn't know yet)
        pending_reveals = [
            f.fact_id for f in self.facts.values()
            if f.audience_knows_since and f.audience_knows_since > query.current_episode
        ][:10]

        return ContextResult(
            query=query,
            facts=results,
            summary=summary,
            relevant_episodes=relevant_eps,
            open_loops=open_loops,
            pending_reveals=pending_reveals,
        )

    def get_audience_knowledge_at(self, episode: int) -> list[Fact]:
        """Get all facts the audience knows at a given episode."""
        fact_ids = self.audience_knowledge.get(episode, [])
        return [self.facts[fid] for fid in fact_ids if fid in self.facts]

    def get_character_knowledge_at(self, character_id: str, episode: int) -> list[Fact]:
        """Get all facts a character knows at a given episode."""
        fact_ids = self.character_knowledge.get(character_id, {}).get(episode, [])
        return [self.facts[fid] for fid in fact_ids if fid in self.facts]

    def add_open_question(self, question_id: str, question: str, episode: int, related_facts: list[str] = None) -> None:
        """Track an open narrative question."""
        self.open_questions[question_id] = {
            "question": question,
            "opened_episode": episode,
            "related_facts": related_facts or [],
            "status": "open",
            "possible_answers": [],
        }

    def resolve_question(self, question_id: str, answer: str, resolved_episode: int) -> bool:
        """Mark an open question as resolved."""
        if question_id in self.open_questions:
            self.open_questions[question_id]["status"] = "resolved"
            self.open_questions[question_id]["answer"] = answer
            self.open_questions[question_id]["resolved_episode"] = resolved_episode
            return True
        return False

    def track_theme_development(self, theme: str, episode: int, development: str, evidence_facts: list[str]) -> None:
        """Track how a theme develops across episodes."""
        self.theme_development[theme].append({
            "episode": episode,
            "development": development,
            "evidence_facts": evidence_facts,
        })

    def get_theme_arc(self, theme: str) -> list[dict[str, Any]]:
        """Get the development arc of a theme."""
        return self.theme_development.get(theme, [])

    def get_memory_stats(self) -> dict[str, Any]:
        """Get statistics about memory contents."""
        status_counts = defaultdict(int)
        type_counts = defaultdict(int)
        importance_counts = defaultdict(int)

        for fact in self.facts.values():
            status_counts[fact.status.value] += 1
            type_counts[fact.fact_type.value] += 1
            importance_counts[fact.importance] += 1

        return {
            "total_facts": len(self.facts),
            "by_status": dict(status_counts),
            "by_type": dict(type_counts),
            "by_importance": dict(importance_counts),
            "open_questions": len([q for q in self.open_questions.values() if q["status"] == "open"]),
            "resolved_questions": len([q for q in self.open_questions.values() if q["status"] == "resolved"]),
            "themes_tracked": len(self.theme_development),
        }

    def export_for_episode(self, episode: int) -> dict[str, Any]:
        """Export all memory relevant to an episode for pipeline context."""
        return {
            "established_facts": [f.model_dump() for f in self.get_facts_for_episode(episode)],
            "audience_knowledge": [f.fact_id for f in self.get_audience_knowledge_at(episode)],
            "open_questions": {k: v for k, v in self.open_questions.items() if v["status"] == "open"},
            "theme_state": {t: v[-1] if v else None for t, v in self.theme_development.items()},
        }


# Default memory
default_memory = SeasonMemory(season_id="season_1")
