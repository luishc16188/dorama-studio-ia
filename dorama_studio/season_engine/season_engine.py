"""
Season Engine - Phase 6
Main orchestrator for generating complete 40-episode seasons.
Integrates all season-level components: arcs, episodes, reveals, characters, continuity, memory.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .character_evolution import CharacterEvolutionPlanner
from .continuity_tracker import ContinuityTracker
from .episode_arc import BeatType, EpisodeArc, EpisodeBeat
from .reveal_scheduler import Reveal, RevealScheduler
from .season_arc import MajorReveal, SeasonAct, SeasonArc
from .season_memory import SeasonMemory


class SeasonPlan(BaseModel):
    """Complete production plan for a season."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid", arbitrary_types_allowed=True)

    season_id: str
    project_id: str
    season_number: int = 1

    # Core structures
    season_arc: SeasonArc
    episode_arcs: dict[str, EpisodeArc] = Field(default_factory=dict)  # episode_id -> EpisodeArc

    # Supporting systems
    reveal_scheduler: RevealScheduler
    character_planner: CharacterEvolutionPlanner
    continuity_tracker: ContinuityTracker
    season_memory: SeasonMemory

    # Production metadata
    total_episodes: int = 40
    genre: str
    subgenre: str | None = None
    target_duration_sec: int = 90

    # Quality targets
    target_viral_score: float = 0.85
    target_quality_score: float = 90.0
    target_continuity_errors: int = 0

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def get_episode_arc(self, episode_number: int) -> EpisodeArc | None:
        """Get episode arc by number."""
        ep_id = f"e{episode_number:02d}"
        return self.episode_arcs.get(ep_id)

    def get_next_episode_to_produce(self) -> int | None:
        """Get the next episode number that needs production."""
        for ep in range(1, self.total_episodes + 1):
            ep_id = f"e{ep:02d}"
            if ep_id not in self.episode_arcs:
                return ep
        return None


class SeasonEngine(BaseModel):
    """
    Main engine for generating and managing 40-episode dorama seasons.
    Orchestrates all season-level components.
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid", arbitrary_types_allowed=True)

    project_id: str
    season_id: str
    season_number: int = 1
    total_episodes: int = 40

    # Core components (lazy-initialized)
    _season_arc: SeasonArc | None = None
    _reveal_scheduler: RevealScheduler | None = None
    _character_planner: CharacterEvolutionPlanner | None = None
    _continuity_tracker: ContinuityTracker | None = None
    _season_memory: SeasonMemory | None = None
    planned_episodes: dict[str, EpisodeArc] = Field(default_factory=dict)

    # Configuration
    genre: str = "romance_traicion"
    subgenre: str | None = None
    target_duration_sec: int = 90

    # Progress tracking
    episodes_completed: int = 0
    episodes_planned: int = 0
    current_episode: int = 0

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Callbacks for integration with orchestration pipeline
    on_episode_planned: Any | None = None
    on_episode_validated: Any | None = None
    on_season_completed: Any | None = None

    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize all season components."""
        self._season_arc = SeasonArc(
            season_id=self.season_id,
            season_number=self.season_number,
            total_episodes=self.total_episodes,
            genre=self.genre,
            subgenre=self.subgenre,
            logline="",  # Will be set by generate_season_arc
            central_question="",
            theme="",
        )

        self._reveal_scheduler = RevealScheduler(
            season_id=self.season_id,
            total_episodes=self.total_episodes,
        )

        self._character_planner = CharacterEvolutionPlanner(
            season_id=self.season_id,
            total_episodes=self.total_episodes,
        )

        self._continuity_tracker = ContinuityTracker(
            project_id=self.project_id,
            season_id=self.season_id,
            total_episodes=self.total_episodes,
        )

        self._season_memory = SeasonMemory(
            season_id=self.season_id,
            total_episodes=self.total_episodes,
        )

    @property
    def season_arc(self) -> SeasonArc:
        return self._season_arc

    @property
    def reveal_scheduler(self) -> RevealScheduler:
        return self._reveal_scheduler

    @property
    def character_planner(self) -> CharacterEvolutionPlanner:
        return self._character_planner

    @property
    def continuity_tracker(self) -> ContinuityTracker:
        return self._continuity_tracker

    @property
    def season_memory(self) -> SeasonMemory:
        return self._season_memory

    @property
    def episode_arcs(self) -> dict[str, EpisodeArc]:
        return self.planned_episodes

    # ============================================================
    # Season Generation Methods
    # ============================================================

    def generate_season_arc(
        self,
        logline: str,
        central_question: str,
        theme: str,
        acts: list[dict[str, Any]] | None = None,
        major_reveals: list[dict[str, Any]] | None = None,
    ) -> SeasonArc:
        """
        Generate the complete season arc structure.

        Args:
            logline: One-sentence summary of the season
            central_question: The question the season answers
            theme: Central theme of the season
            acts: Optional custom act configurations
            major_reveals: Optional custom reveal schedule

        Returns:
            Complete SeasonArc
        """
        arc = self._season_arc
        arc.logline = logline
        arc.central_question = central_question
        arc.theme = theme

        # Create default acts if not provided
        if not acts:
            acts = self._default_act_structure()

        for act_data in acts:
            act = SeasonAct(**act_data)
            arc.acts.append(act)

        # Add major reveals
        if not major_reveals:
            major_reveals = self._default_major_reveals()

        for reveal_data in major_reveals:
            reveal = MajorReveal(**reveal_data)
            arc.major_reveals.append(reveal)
            self._reveal_scheduler.schedule_reveal(Reveal(**reveal_data))

        # Auto-schedule standard reveals
        self._reveal_scheduler.auto_schedule_standard_reveals()

        # Validate
        issues = arc.validate_structure()
        if issues:
            raise ValueError(f"Season arc validation failed: {issues}")

        return arc

    def _default_act_structure(self) -> list[dict[str, Any]]:
        """Default 4-act structure scaled to total_episodes."""
        # Base structure for 40 episodes
        base_ranges = [
            (1, 10),   # Setup
            (11, 25),  # Confrontation
            (26, 35),  # Climax
            (36, 40),  # Resolution
        ]
        base_themes = [
            "Establish world, characters, inciting incident",
            "Rising action, complications, first major reveal",
            "Major revelations, peak tension, transformation",
            "Payoffs, closure, new equilibrium",
        ]
        base_major_beats = [
            ["inciting_incident", "first_threshold", "meet_antagonist"],
            ["betrayal_reveal", "power_discovery", "midpoint_climax"],
            ["identity_reveal", "power_mastery", "dark_night", "transformation"],
            ["final_confrontation", "sacrifice", "new_equilibrium", "s2_hook"],
        ]
        base_emotional_arcs = [
            "curiosity -> intrigue -> commitment",
            "confidence -> doubt -> desperation",
            "despair -> hope -> determination",
            "resolution -> catharsis -> anticipation",
        ]
        base_stakes_escalations = [
            "personal -> relational",
            "relational -> global",
            "global -> existential",
            "resolved -> new_questions",
        ]

        acts = []
        for i, (base_start, base_end) in enumerate(base_ranges):
            # Scale to total_episodes
            start = max(1, int(round(base_start * (self.total_episodes / 40.0))))
            end = min(self.total_episodes, int(round(base_end * (self.total_episodes / 40.0))))
            # Ensure at least 1 episode per act
            if end < start:
                end = start
            acts.append({
                "act_number": i + 1,
                "act_type": ["setup", "confrontation", "climax", "resolution"][i],
                "episode_range": (start, end),
                "theme": base_themes[i],
                "major_beats": base_major_beats[i],
                "emotional_arc": base_emotional_arcs[i],
                "stakes_escalation": base_stakes_escalations[i],
            })
        return acts

    def _default_major_reveals(self) -> list[dict[str, Any]]:
        """Default major reveal schedule for a 40-episode season."""
        return [
            {"reveal_id": "identity_1", "reveal_type": "identity", "description": "Protagonist's true lineage", "episode": 5, "foreshadowing_strength": 0.6, "impact_level": "personal"},
            {"reveal_id": "betrayal_1", "reveal_type": "betrayal", "description": "Trusted ally is antagonist", "episode": 8, "foreshadowing_strength": 0.7, "impact_level": "relational"},
            {"reveal_id": "power_1", "reveal_type": "power_source", "description": "True nature of power source", "episode": 15, "foreshadowing_strength": 0.8, "impact_level": "global"},
            {"reveal_id": "conspiracy_1", "reveal_type": "conspiracy", "description": "Hidden organization controlling events", "episode": 18, "foreshadowing_strength": 0.7, "impact_level": "global"},
            {"reveal_id": "betrayal_2", "reveal_type": "double_agent", "description": "Key ally playing both sides", "episode": 22, "foreshadowing_strength": 0.8, "impact_level": "relational"},
            {"reveal_id": "identity_2", "reveal_type": "identity", "description": "Protagonist's true identity", "episode": 28, "foreshadowing_strength": 0.9, "impact_level": "personal"},
            {"reveal_id": "power_2", "reveal_type": "power_source", "description": "How to control/defeat the power", "episode": 30, "foreshadowing_strength": 0.9, "impact_level": "global"},
            {"reveal_id": "fake_death", "reveal_type": "fake_death", "description": "Presumed dead character returns", "episode": 32, "foreshadowing_strength": 0.85, "impact_level": "relational"},
            {"reveal_id": "conspiracy_2", "reveal_type": "conspiracy", "description": "Mastermind's true identity", "episode": 37, "foreshadowing_strength": 0.8, "impact_level": "global"},
            {"reveal_id": "prophecy", "reveal_type": "prophecy_twist", "description": "Prophecy fulfilled unexpectedly", "episode": 39, "foreshadowing_strength": 0.9, "impact_level": "global"},
        ]

    def plan_episode(self, episode_number: int) -> EpisodeArc:
        """
        Plan a single episode within the season context.

        Args:
            episode_number: Episode number (1-40)

        Returns:
            Complete EpisodeArc
        """
        if not (1 <= episode_number <= self.total_episodes):
            raise ValueError(f"Episode number must be 1-{self.total_episodes}")

        # Check if already planned
        ep_id = f"e{episode_number:02d}"
        if ep_id in self.planned_episodes:
            return self.planned_episodes[ep_id]

        # Get act context
        act = self.season_arc.get_act_for_episode(episode_number)
        if not act:
            raise ValueError(f"Episode {episode_number} not in any act")

        # Get scheduled reveals for this episode
        reveals = self._reveal_scheduler.get_reveals_for_episode(episode_number)
        reveal_ids = [r.reveal_id for r in reveals]

        # Get open loops
        open_loops = self._reveal_scheduler.get_open_loops_at_episode(episode_number)

        # Build episode arc
        episode_arc = EpisodeArc(
            episode_id=ep_id,
            episode_number=episode_number,
            season_id=self.season_id,
            act_number=self._get_act_number(episode_number),
            season_arc_ref=self.season_arc.season_id,
            hook_category=self._select_hook_category(episode_number),
            core_conflict=self._derive_core_conflict(episode_number),
            twist=self._plan_twist(episode_number),
            cliffhanger=self._plan_cliffhanger(episode_number),
            cta_type=self._select_cta_type(episode_number),
            reveals=reveal_ids,
            opens_loops=[l.loop_id for l in open_loops if l.status == "open"],
            closes_loops=[l.loop_id for l in open_loops if l.expected_close_episode == episode_number],
        )

        # Generate 9 beats
        self._generate_beats(episode_arc, episode_number)

        # Validate
        issues = episode_arc.validate_episode()
        if issues:
            # Log warnings but don't fail
            pass

        # Store
        self.planned_episodes[ep_id] = episode_arc
        self.episodes_planned += 1

        # Callback
        if self.on_episode_planned:
            self.on_episode_planned(episode_arc)

        return episode_arc

    def _get_act_number(self, episode: int) -> int:
        """Get act number for episode."""
        if episode <= 10: return 1
        elif episode <= 25: return 2
        elif episode <= 35: return 3
        else: return 4

    def _select_hook_category(self, episode: int) -> str:
        """Select hook category based on episode position."""
        categories = [
            "visual_shock", "identity_shock", "betrayal", "threat",
            "impossible_romance", "moral_dilemma", "power_reveal",
            "humiliation", "revelation", "question"
        ]
        # Cycle through with some variation
        idx = (episode - 1) % len(categories)
        return categories[idx]

    def _derive_core_conflict(self, episode: int) -> str:
        """Derive core conflict for episode based on season arc and act."""
        act = self.season_arc.get_act_for_episode(episode)
        if not act:
            return "Conflict undefined"

        act_conflicts = {
            1: "Establishing the world and the inciting incident",
            2: "Rising complications and first major betrayal",
            3: "Peak confrontation and transformation",
            4: "Final resolution and new equilibrium",
        }
        return act_conflicts.get(act.act_number, "Conflict undefined")

    def _plan_twist(self, episode: int) -> str:
        """Plan the twist for this episode."""
        # Check for scheduled reveals
        reveals = self._reveal_scheduler.get_reveals_for_episode(episode)
        if reveals:
            return reveals[0].description

        # Default twists by episode position
        twists = [
            "Secret ally revealed", "Hidden agenda exposed", "Power awakens",
            "Memory returns", "Alliance shattered", "Identity questioned",
            "Power awakens", "Truth revealed", "Final choice",
        ]
        idx = (episode - 1) % len(twists)
        return twists[idx]

    def _plan_cliffhanger(self, episode: int) -> str:
        """Plan cliffhanger for episode."""
        # Last episode of season
        if episode == self.total_episodes:
            return "New threat emerges from unexpected quarter"

        # Act boundaries
        if episode in [10, 25, 35]:
            return "Major act-ending revelation changes everything"

        # Mid-act cliffhangers
        cliffhangers = [
            "Character makes impossible choice",
            "Unexpected arrival changes everything",
            "Secret discovered at worst moment",
            "Ally reveals true allegiance",
            "Power fails at critical moment",
            "Past returns to haunt present",
        ]
        idx = (episode - 1) % len(cliffhangers)
        return cliffhangers[idx]

    def _select_cta_type(self, episode: int) -> str:
        """Select CTA type for episode."""
        cta_cycle = [
            "moral_dilemma", "identity_tease", "revenge_choice",
            "team_war", "question_tribal", "protect_loved_one",
            "sacrifice_choice", "moral_dilemma", "identity_tease",
        ]
        idx = (episode - 1) % len(cta_cycle)
        return cta_cycle[idx]

    def _generate_beats(self, episode_arc: EpisodeArc, episode_number: int) -> None:
        """Generate the 9 beats for an episode."""
        beat_configs = [
            {"type": "hook", "duration": 10, "emotional": "shock", "info": "reveal"},
            {"type": "context", "duration": 10, "emotional": "curiosity", "info": "partial"},
            {"type": "problem", "duration": 10, "emotional": "tension", "info": "reveal"},
            {"type": "escalation", "duration": 10, "emotional": "urgency", "info": "withhold"},
            {"type": "twist_1", "duration": 10, "emotional": "shock", "info": "reveal"},
            {"type": "conflict_2", "duration": 10, "emotional": "desperation", "info": "partial"},
            {"type": "revelation", "duration": 10, "emotional": "catharsis", "info": "reveal"},
            {"type": "cliffhanger", "duration": 10, "emotional": "suspense", "info": "withhold"},
            {"type": "cta", "duration": 10, "emotional": "engagement", "info": "question"},
        ]

        for i, config in enumerate(beat_configs):
            beat = EpisodeBeat(
                beat_type=BeatType(config["type"]),
                beat_number=i + 1,
                duration_sec=config["duration"],
                narrative_goal=self._beat_narrative_goal(config["type"], episode_number),
                emotional_target=config["emotional"],
                information_delta=config["info"],
                action=self._beat_action(config["type"]),
                character_ids=self._beat_characters(episode_number),
            )
            episode_arc.add_beat(beat)

        episode_arc._recalc_timing()

    def _beat_narrative_goal(self, beat_type: str, episode: int) -> str:
        goals = {
            "hook": "Grab attention with impossible visual + sub-bass",
            "context": "Establish world rules and character baseline",
            "problem": "Inciting incident disrupts status quo",
            "escalation": "Stakes rise, protagonist pressured",
            "twist_1": "Revelation recontextualizes everything",
            "conflict_2": "New complication from unexpected angle",
            "revelation": "Truth revealed, emotional payoff",
            "cliffhanger": "Impossible choice, visual punch, sub-bass",
            "cta": "Moral question to audience, loop to next ep",
        }
        return goals.get(beat_type, "Advance narrative")

    def _beat_action(self, beat_type: str) -> str:
        actions = {
            "hook": "protagonist discovers impossible object",
            "context": "protagonist navigates established world",
            "problem": "antagonist makes first move against protagonist",
            "escalation": "protagonist forced into corner",
            "twist_1": "protagonist discovers impossible truth",
            "conflict_2": "antagonist reveals true power",
            "revelation": "protagonist confronts truth",
            "cliffhanger": "protagonist faces impossible choice",
            "cta": "protagonist addresses audience directly",
        }
        return actions.get(beat_type, "character acts")

    def _beat_characters(self, episode: int) -> list[str]:
        """Get character IDs for this episode's beats."""
        # In production, would be derived from character planner
        return ["protagonist", "antagonist", "deuteragonist"]

    # ============================================================
    # Validation & Quality
    # ============================================================

    def validate_season(self) -> dict[str, Any]:
        """Run comprehensive season validation."""
        results = {
            "season_arc": self.season_arc.validate_structure(),
            "reveal_schedule": self._reveal_scheduler.validate_schedule(),
            "character_arcs": self._character_planner.validate_all_arcs(),
            "continuity": [],
            "episodes": {},
            "overall": "pass",
        }

        # Validate each planned episode
        for ep_num in range(1, self.total_episodes + 1):
            ep_id = f"e{ep_num:02d}"
            if ep_id in self.planned_episodes:
                results["episodes"][ep_num] = self.planned_episodes[ep_id].validate_episode()

        # Run continuity check on all episodes
        for ep in range(1, self.total_episodes + 1):
            errors = self._continuity_tracker.validate_continuity(ep)
            if errors:
                results["continuity"].extend([e.model_dump() for e in errors])

        # Determine overall status
        all_issues = (
            len(results["season_arc"]) +
            len(results["reveal_schedule"]) +
            sum(len(v) for v in results["character_arcs"].values()) +
            sum(len(v) for v in results["episodes"].values()) +
            len(results["continuity"])
        )

        results["overall"] = "pass" if all_issues == 0 else "fail"
        results["total_issues"] = all_issues

        return results

    def validate_episode(self, episode_number: int) -> list[str]:
        """Validate a specific episode."""
        ep_id = f"e{episode_number:02d}"
        if ep_id not in self.planned_episodes:
            return [f"Episode {episode_number} not planned"]
        return self.planned_episodes[ep_id].validate_episode()

    # ============================================================
    # Production Integration
    # ============================================================

    def get_production_context(self, episode_number: int) -> dict[str, Any]:
        """Get all context needed for episode production."""
        ep_id = f"e{episode_number:02d}"
        episode_arc = self.planned_episodes.get(ep_id)

        if not episode_arc:
            episode_arc = self.plan_episode(episode_number)

        # Get memory context
        memory_context = self._season_memory.export_for_episode(episode_number)

        # Get character states
        character_states = {}
        for char_id in self._character_planner.characters:
            state = self._continuity_tracker.get_character_state(char_id, episode_number)
            if state:
                character_states[char_id] = state.model_dump()

        # Get scheduled reveals
        reveals = self._reveal_scheduler.get_reveals_for_episode(episode_number)

        return {
            "episode_arc": episode_arc.model_dump() if episode_arc else None,
            "season_arc": self.season_arc.model_dump(),
            "reveals": [r.model_dump() for r in reveals],
            "memory_context": memory_context,
            "character_states": character_states,
            "continuity_rules": self._continuity_tracker.rules,
            "reveal_schedule": {
                "upcoming": [
                    {"id": r.reveal_id, "episode": r.episode, "type": r.reveal_type}
                    for r in self._reveal_scheduler.get_upcoming_reveals(episode_number, 5)
                ],
            },
        }

    def advance_episode(self, episode_number: int) -> None:
        """Mark episode as completed and advance state."""
        self.current_episode = episode_number
        self.episodes_completed = episode_number
        self.updated_at = datetime.utcnow()

        # Update character evolution
        for char_id, arc in self._character_planner.characters.items():
            expected_stage = arc.get_stage_for_episode(episode_number + 1)
            if arc.current_stage != expected_stage:
                arc.advance_stage(episode_number + 1, expected_stage, f"Episode {episode_number} completed")

        # Update continuity tracker with episode events
        # (Would be called with actual episode events in production)

        # Update memory with episode facts
        # (Would be called with actual episode facts in production)

    def export_season_plan(self) -> dict[str, Any]:
        """Export complete season plan for production."""
        return {
            "project_id": self.project_id,
            "season_id": self.season_id,
            "season_number": self.season_number,
            "total_episodes": self.total_episodes,
            "genre": self.genre,
            "subgenre": self.subgenre,
            "season_arc": self.season_arc.model_dump(),
            "episode_arcs": {k: v.model_dump() for k, v in self.planned_episodes.items()},
            "reveal_schedule": {
                "reveals": {k: v.model_dump() for k, v in self._reveal_scheduler.reveals.items()},
                "open_loops": {k: v.model_dump() for k, v in self._reveal_scheduler.open_loops.items()},
                "density_report": self._reveal_scheduler.get_density_report(),
            },
            "character_arcs": {k: v.model_dump() for k, v in self._character_planner.characters.items()},
            "continuity_errors": [e.model_dump() for e in self._continuity_tracker.errors],
            "season_memory": self._season_memory.get_memory_stats(),
            "validation": self.validate_season(),
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "episodes_planned": len(self.planned_episodes),
                "episodes_completed": self.episodes_completed,
            },
        }


# Default engine
default_engine = SeasonEngine(
    project_id="proj_1",
    season_id="season_1",
    season_number=1,
)
